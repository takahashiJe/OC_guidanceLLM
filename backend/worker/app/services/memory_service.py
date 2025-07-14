import logging
from typing import List
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sqlalchemy.orm import Session
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_community.embeddings import OllamaEmbeddings
from shared.db.crud import get_history_by_session_id, create_history_record

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, db_session: Session, vectorstore_memory):
        """
        サービスを初期化します。
        DBセッションとベクトルストアに依存します。
        """
        self.db_session = db_session
        self.vectorstore_memory = vectorstore_memory # 長期記憶のために予約
        self.embedder = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://ollama:11434"
        )

    def get_history(self, user_id: int, session_id: str, latest_input: str) -> List[BaseMessage]:
        """
        短期記憶（DB）から会話履歴を取得し、意味的に重複する内容を排除して返します。
        """
        short_term_memory = self._get_short_term_memory(user_id, session_id)
        logger.info(f"短期記憶から {len(short_term_memory)} 件のメッセージを取得しました。")

        # 長期記憶の処理は今回は省略
        long_term_memory = []

        combined_history = long_term_memory + short_term_memory
        if not combined_history:
            return []

        logger.info(f"統合前の履歴は {len(combined_history)} 件です。意味的な重複排除を開始します。")
        final_history = self._semantic_deduplication(combined_history)
        logger.info(f"重複排除後の最終的な履歴は {len(final_history)} 件です。")
        return final_history

    def _get_short_term_memory(self, user_id: int, session_id: str) -> List[BaseMessage]:
        """DBから直近の会話履歴を取得します"""
        history_records = get_history_by_session_id(self.db_session, session_id, user_id)
        history_records.reverse()

        history: List[BaseMessage] = []
        for record in history_records:
            history.append(HumanMessage(content=record.human_message))
            history.append(AIMessage(content=record.ai_message))
        return history

    def _semantic_deduplication(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        if len(messages) < 2:
            return messages

        contents = [msg.content for msg in messages]
        logger.info(f"{len(contents)}件のメッセージのエンべディングをOllamaにリクエストします...")
        embeddings_list = self.embedder.embed_documents(contents)
        embeddings = np.array(embeddings_list)
        logger.info("エンべディングが完了しました。")

        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.2,
            metric='cosine',
            linkage='average'
        ).fit(embeddings)

        clusters = {}
        for i, label in enumerate(clustering.labels_):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(i)

        deduplicated_indices = []
        for _, indices in clusters.items():
            representative_index = max(indices)
            deduplicated_indices.append(representative_index)

        deduplicated_indices.sort()
        final_messages = [messages[i] for i in deduplicated_indices]
        return final_messages

    def save_history(self, user_id: int, session_id: str, turn: int, human_message: str, ai_message: str):
        """会話のやりとりをDBに保存します"""
        create_history_record(
            db=self.db_session,
            user_id=user_id,
            session_id=session_id,
            turn=turn,
            human_message=human_message,
            ai_message=ai_message
        )
        logger.info(f"会話履歴を保存しました (Turn: {turn})")