# backend/worker/app/tasks.py

import os
from contextlib import contextmanager

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from sqlalchemy.orm import Session

# Celery, DB, Service, Graphの各コンポーネントをインポート
from shared.celery_app import celery_app
from shared.db.session import SessionLocal
from shared.services.memory_service import MemoryService
from .graph.build import build_graph, AgentState # グラフと状態定義をインポート

# --- Worker起動時に一度だけ読み込む設定 ---
llm = ChatOllama(
    model="qwen2.5:32b-instruct",
        # model="gemma3:27b-it-qat",
        # model="gemma3:27b",
        # model="llama3:70b",
        # model="elyza-jp-chat",
    base_url="http://ollama:11434",
)

EMBEDDINGS = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

CHROMA_KNOWLEDGE_PATH = "/app/data/vectorstore_knowledge"
CHROMA_MEMORY_PATH = "/app/data/vectorstore_memory"
vectorstore_knowledge = Chroma(
    persist_directory=CHROMA_KNOWLEDGE_PATH,
    embedding_function=EMBEDDINGS,
)
rag_retriever = vectorstore_knowledge.as_retriever(search_kwargs={"k": 3})
vectorstore_memory = Chroma(
    persist_directory=CHROMA_MEMORY_PATH,
    embedding_function=EMBEDDINGS,
)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Celeryタスクの定義 (新アプローチ版) ---

@celery_app.task(name='worker.app.tasks.run_chat_graph')
def run_chat_graph(user_id: int, session_id: str, user_input: str) -> str:
    """
    API Gatewayから呼び出されるメインの対話処理タスク。
    記憶の取得・保存をこのタスク内で行い、グラフは思考に専念する。
    """
    print(f"---TASK: 開始 (user_id: {user_id}, session_id: {session_id})---")
    
    final_response = "エラーにより応答を生成できませんでした。"
    with get_db() as db:
        # 1. 必要なサービスとグラフをインスタンス化
        memory_service = MemoryService(db_session=db, vectorstore_memory=vectorstore_memory)
        app = build_graph(rag_retriever=rag_retriever, llm=llm)

        # 2. 【事前準備】記憶を取得する
        print("---TASK: 記憶を取得中---")
        history_messages = memory_service.get_history(
            user_id=user_id,
            session_id=session_id,
            latest_input=user_input,
        )
        
        # 3. グラフを実行するための初期状態を定義
        #    今回は準備した記憶(history_messages)を直接渡す
        initial_state: AgentState = {
            "user_input": user_input,
            "messages": history_messages + [("human", user_input)],
        }
        
        # 4. 【思考依頼】グラフを実行
        final_state = app.invoke(initial_state)
        final_response = final_state.get("llm_response", final_response)
        
        # 5. 【事後処理】新しい会話を記憶に保存する
        print("---TASK: 会話を記憶に保存中---")
        last_turn = db.execute(
            "SELECT MAX(turn) FROM conversation_history WHERE session_id = :session_id",
            {"session_id": session_id}
        ).scalar()
        current_turn = (last_turn or 0) + 1

        memory_service.save_history(
            user_id=user_id,
            session_id=session_id,
            turn=current_turn,
            human_message=user_input,
            ai_message=final_response,
        )

    print(f"---TASK: 終了 (応答: {final_response})---")
    return final_response

