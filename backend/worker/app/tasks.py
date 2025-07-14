# backend/worker/app/tasks.py

from contextlib import contextmanager

from sqlalchemy import text
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from sqlalchemy.orm import Session

from shared.celery_app import celery_app
from shared.db.session import SessionLocal
# worker配下に移動したMemoryServiceをインポート
from .services.memory_service import MemoryService
from .graph.build import build_graph, AgentState

# --- Worker起動時に一度だけ読み込む設定 ---
llm = ChatOllama(
        model="qwen2.5:32b-instruct",
        # model="gemma3:27b-it-qat",
        # model="gemma3:27b",
        # model="llama3:70b",
        # model="elyza-jp-chat",
        base_url="http://ollama:11434",
        temperature=0.7
        )

EMBEDDINGS = OllamaEmbeddings(model="nomic-embed-text", base_url="http://ollama:11434")
CHROMA_KNOWLEDGE_PATH = "/app/data/vectorstore_knowledge"
CHROMA_MEMORY_PATH = "/app/data/vectorstore_memory"
vectorstore_knowledge = Chroma(persist_directory=CHROMA_KNOWLEDGE_PATH, embedding_function=EMBEDDINGS)
rag_retriever = vectorstore_knowledge.as_retriever(search_kwargs={"k": 5}) # 検索結果を少し増やす
vectorstore_memory = Chroma(persist_directory=CHROMA_MEMORY_PATH, embedding_function=EMBEDDINGS)

# --- DBセッションのコンテキストマネージャ ---
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Celeryタスクの定義 (最終版) ---
@celery_app.task(name='worker.app.tasks.run_chat_graph')
def run_chat_graph(user_id: int, session_id: str, user_input: str) -> str:
    """
    AIの思考パイプラインを呼び出し、対話処理全体を管理するタスク。
    """
    print(f"---TASK: 開始 (user_id: {user_id}, session_id: {session_id})---")
    
    final_response = "エラーにより応答を生成できませんでした。"
    with get_db() as db:
        # 1. 【事前準備】記憶サービスを準備し、過去の会話履歴を取得
        memory_service = MemoryService(db_session=db, vectorstore_memory=vectorstore_memory)
        history_messages = memory_service.get_history(user_id=user_id, session_id=session_id)
        
        # 2. AIの思考パイプライン（グラフ）をインスタンス化
        app = build_graph(rag_retriever=rag_retriever, llm=llm)

        # 3. パイプラインを実行するための初期状態を定義
        initial_state = AgentState(
            user_input=user_input,
            history_messages=history_messages,
        )
        
        # 4. 【思考依頼】グラフ（パイプライン）を実行
        final_state = app.invoke(initial_state)
        # 最終的な応答を 'final_response' キーから取得
        final_response = final_state.get("final_response", final_response)
        
        # 5. 【事後処理】今回のやり取りを短期・長期記憶に保存
        print("---TASK: 会話を記憶に保存中---")
        last_turn = db.execute(
            text("SELECT MAX(turn) FROM conversation_history WHERE session_id = :session_id"),
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
