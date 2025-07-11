# backend/worker/app/services/memory_service.py

import logging
from typing import List
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sqlalchemy.orm import Session
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_community.embeddings import OllamaEmbeddings # OllamaEmbeddings をインポート

from shared.db.models import ChatMessage
from shared.db.db_service import get_messages_by_session_id

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, session: Session, session_id: str, llm_service):
        self.session = session
        self.session_id = session_id
        self.llm_service = llm_service
        self.embedder = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://ollama:11434"
        )

    def get_history(self) -> List[BaseMessage]:
        """
        短期記憶（DB）と長期記憶から会話履歴を取得し、
        意味的に重複する内容を排除して統合した履歴を返す。
        """
        # 1. 短期記憶の取得 (直近の会話履歴)
        short_term_memory = self._get_short_term_memory()
        logger.info(f"短期記憶から {len(short_term_memory)} 件のメッセージを取得しました。")

        # 2. 長期記憶の取得（この実装ではダミー）
        long_term_memory = self._get_long_term_memory()
        logger.info(f"長期記憶から {len(long_term_memory)} 件のメッセージを取得しました。")
        
        # 3. 履歴の統合と意味的な重複排除
        combined_history = long_term_memory + short_term_memory
        if not combined_history:
            return []

        logger.info(f"統合前の履歴は {len(combined_history)} 件です。意味的な重複排除を開始します。")
        final_history = self._semantic_deduplication(combined_history)
        logger.info(f"重複排除後の最終的な履歴は {len(final_history)} 件です。")

        return final_history

    def _get_short_term_memory(self) -> List[BaseMessage]:
        """DBから直近の会話履歴を取得する"""
        messages = get_messages_by_session_id(self.session, self.session_id)
        history: List[BaseMessage] = []
        for msg in messages:
            if msg.sender == "human":
                history.append(HumanMessage(content=msg.message))
            elif msg.sender == "ai":
                history.append(AIMessage(content=msg.message))
        return history
    
    def _get_long_term_memory(self) -> List[BaseMessage]:
        """ベクトルストアなどから長期記憶を取得する（この実装ではダミー）"""
        return []

    def _semantic_deduplication(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        OllamaEmbeddingsを使用してメッセージの意味的な重複を排除する。
        類似したメッセージをクラスタリングし、各クラスタから1つの代表メッセージを選ぶ。
        """
        if len(messages) < 2:
            return messages

        contents = [msg.content for msg in messages]
        
        # LangChainのOllamaEmbeddingsを使ってドキュメントをエンコーディング
        logger.info(f"{len(contents)}件のメッセージのエンべディングをOllamaにリクエストします...")
        embeddings_list = self.embedder.embed_documents(contents)
        embeddings = np.array(embeddings_list)
        logger.info("エンべディングが完了しました。")

        # 凝集型クラスタリングを実行
        # distance_threshold: 類似度の閾値。値が小さいほど「似ている」と判定する基準が厳しくなる
        # (コサイン距離 = 1 - コサイン類似度)
        # 例えば、類似度0.9以上を同一クラスタとしたい場合、距離の閾値は 1 - 0.9 = 0.1 となる
        clustering = AgglomerativeClustering(
            n_clusters=None, 
            distance_threshold=0.2, # コサイン類似度0.8以上を同一クラスタとみなす
            metric='cosine', 
            linkage='average'
        ).fit(embeddings)
        
        clusters = {}
        for i, label in enumerate(clustering.labels_):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(i)

        # 各クラスタから代表メッセージを選択
        deduplicated_indices = []
        for label, indices in clusters.items():
            # クラスタ内で最新（リストの後方）のメッセージを代表として選択
            representative_index = max(indices)
            deduplicated_indices.append(representative_index)
        
        # 元の順序を保つためにインデックスをソート
        deduplicated_indices.sort()
        
        final_messages = [messages[i] for i in deduplicated_indices]
        return final_messages

    def save_message(self, human_message: str, ai_message: str):
        """会話のやりとりをDBに保存する"""
        human_msg_db = ChatMessage(
            session_id=self.session_id, sender="human", message=human_message
        )
        ai_msg_db = ChatMessage(
            session_id=self.session_id, sender="ai", message=ai_message
        )
        self.session.add(human_msg_db)
        self.session.add(ai_msg_db)
        self.session.commit()