import logging
from typing import List
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sqlalchemy.orm import Session
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_community.embeddings import OllamaEmbeddings

# ★★★ 修正点: 正しいモデルとCRUD関数をインポート ★★★
from backend.shared.db.models import ConversationHistory
from backend.shared.db.crud import get_history_by_session_id, create_history_record

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryService:
    # ★★★ 修正点: __init__の引数を変更 ★★★
    def __init__(self, session: Session, user_id: int, session_id: str):
        self.session = session
        self.user_id = user_id
        self.session_id = session_id
        self.embedder = OllamaEmbeddings(
            model="nomic-embed-text",
            # docker-compose.ymlのサービス名に合わせる
            base_url="http://ollama:11434"
        )

    def get_history(self) -> List[BaseMessage]:
        """
        短期記憶（DB）から会話履歴を取得し、意味的に重複する内容を排除して返す。
        """
        short_term_memory = self._get_short_term_memory()
        logger.info(f"短期記憶から {len(short_term_memory)} 件のメッセージを取得しました。")

        # 長期記憶の処理は省略
        long_term_memory = []

        combined_history = long_term_memory + short_term_memory
        if not combined_history:
            return []

        logger.info(f"統合前の履歴は {len(combined_history)} 件です。意味的な重複排除を開始します。")
        final_history = self._semantic_deduplication(combined_history)
        logger.info(f"重複排除後の最終的な履歴は {len(final_history)} 件です。")

        return final_history

    def _get_short_term_memory(self) -> List[BaseMessage]:
        """DBから直近の会話履歴を取得する"""
        # ★★★ 修正点: 新しいCRUD関数を利用 ★★★
        history_records = get_history_by_session_id(self.session, self.session_id, self.user_id)
        # 順番を元に戻す(古い順)
        history_records.reverse()

        history: List[BaseMessage] = []
        for record in history_records:
            # ★★★ 修正点: ConversationHistoryモデルの属性を利用 ★★★
            history.append(HumanMessage(content=record.human_message))
            history.append(AIMessage(content=record.ai_message))
        return history

    def _get_long_term_memory(self) -> List[BaseMessage]:
        """ベクトルストアなどから長期記憶を取得する（この実装ではダミー）"""
        return []

    def _semantic_deduplication(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        # (このメソッドは変更なし)
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
        for label, indices in clusters.items():
            representative_index = max(indices)
            deduplicated_indices.append(representative_index)

        deduplicated_indices.sort()
        final_messages = [messages[i] for i in deduplicated_indices]
        return final_messages

    def save_history(self, human_message: str, ai_message: str, turn: int):
        """会話のやりとりをDBに保存する"""
        # ★★★ 修正点: 新しいCRUD関数を利用 ★★★
        create_history_record(
            db=self.session,
            user_id=self.user_id,
            session_id=self.session_id,
            turn=turn,
            human_message=human_message,
            ai_message=ai_message
        )
        logger.info(f"会話履歴を保存しました (Turn: {turn})")