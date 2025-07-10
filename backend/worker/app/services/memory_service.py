# backend/worker/app/services/memory_service.py

from typing import List
from sqlalchemy.orm import Session
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from backend.worker.app.db.models import ConversationHistory

class MemoryService:
    """
    会話の短期記憶（MySQL）と長期記憶（ChromaDB）を管理するサービスクラス。
    """
    def __init__(self, db_session: Session, vectorstore_memory: Chroma):
        self.db = db_session
        self.vectorstore_memory = vectorstore_memory

    def get_history(
        self,
        user_id: int,
        session_id: str,
        latest_input: str,
        short_term_k: int = 5,
        long_term_k: int = 3,
    ) -> List[BaseMessage]:
        """
        指定されたユーザーの会話履歴を取得する。
        """
        # 1. 短期記憶の取得 (現在のセッションの直近の文脈)
        short_term_results = (
            self.db.query(ConversationHistory)
            .filter(ConversationHistory.session_id == session_id)
            .order_by(ConversationHistory.turn.desc())
            .limit(short_term_k)
            .all()
        )
        short_term_results.reverse()
        
        short_term_memory: List[BaseMessage] = []
        for res in short_term_results:
            short_term_memory.append(HumanMessage(content=res.human_message))
            short_term_memory.append(AIMessage(content=res.ai_message))

        # 2. 長期記憶の取得 (過去のセッションを含む、関連性の高い会話)
        long_term_docs = self.vectorstore_memory.similarity_search(
            query=latest_input,
            k=long_term_k,
            filter={"user_id": user_id}
        )
        
        long_term_memory: List[BaseMessage] = []
        for doc in long_term_docs:
            parts = doc.page_content.split("\nAI: ")
            if len(parts) == 2:
                human_part = parts[0].replace("Human: ", "")
                ai_part = parts[1]
                long_term_memory.append(HumanMessage(content=human_part))
                long_term_memory.append(AIMessage(content=ai_part))

        # 3. 履歴の統合
        combined_history = long_term_memory + short_term_memory
        final_history = []
        seen = set()
        for msg in reversed(combined_history):
            msg_tuple = (type(msg).__name__, msg.content)
            if msg_tuple not in seen:
                final_history.append(msg)
                seen.add(msg_tuple)
        final_history.reverse()
        return final_history

    def save_history(
        self,
        user_id: int,
        session_id: str,
        turn: int,
        human_message: str,
        ai_message: str,
    ):
        """
        新しい会話をMySQLとChromaDBの両方に保存する。
        """
        new_history_record = ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            turn=turn,
            human_message=human_message,
            ai_message=ai_message,
        )
        self.db.add(new_history_record)
        self.db.commit()

        doc_content = f"Human: {human_message}\nAI: {ai_message}"
        doc = Document(
            page_content=doc_content,
            metadata={"user_id": user_id, "session_id": session_id, "turn": turn}
        )
        self.vectorstore_memory.add_documents([doc])
