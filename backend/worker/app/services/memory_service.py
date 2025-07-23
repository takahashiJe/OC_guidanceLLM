# backend/worker/app/services/memory_service.py

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
        self.vectorstore_memory = vectorstore_memory # 長期記憶用ベクトルストア
        self.embedder = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://ollama:11434"
        )

    def get_history(self, user_id: int, session_id: str) -> List[BaseMessage]:
        """
        短期記憶（DB）から会話履歴を取得します。
        ※このデモでは、意味的重複排除や長期記憶からの取得は省略し、
        　短期記憶のみを返すシンプルな実装とします。
        """
        logger.info(f"短期記憶からメッセージを取得中 (Session ID: {session_id})")
        return self._get_short_term_memory(user_id, session_id)

    def _get_short_term_memory(self, user_id: int, session_id: str) -> List[BaseMessage]:
        """DBから直近の会話履歴を取得します"""
        history_records = get_history_by_session_id(self.db_session, session_id, user_id)
        history_records.reverse()

        history: List[BaseMessage] = []
        for record in history_records:
            history.append(HumanMessage(content=record.human_message))
            history.append(AIMessage(content=record.ai_message))
        return history

    def save_history(self, user_id: int, session_id: str, turn: int, human_message: str, ai_message: str):
        """
        会話のやりとりを短期記憶（DB）と長期記憶（ベクトルストア）の両方に保存します。
        """
        # --- 1. 短期記憶（リレーショナルDB）への保存 ---
        create_history_record(
            db=self.db_session,
            user_id=user_id,
            session_id=session_id,
            turn=turn,
            human_message=human_message,
            ai_message=ai_message
        )
        logger.info(f"短期記憶（DB）に会話履歴を保存しました (Turn: {turn})")

        # --- 2. 長期記憶（ベクトルストア）への保存 ---
        long_term_memory_text = f"ユーザーの質問: {human_message}\nAIの応答: {ai_message}"
        self.vectorstore_memory.add_texts(
            texts=[long_term_memory_text],
            metadatas=[
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "turn": turn,
                    "type": "conversation_history" # 知識と区別するためのメタデータ
                }
            ]
        )
        logger.info(f"長期記憶（ベクトルストア）に会話履歴を保存しました (Turn: {turn})")

