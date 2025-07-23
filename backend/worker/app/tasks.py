# backend/worker/app/tasks.py

from contextlib import contextmanager
from sqlalchemy import text
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from sqlalchemy.orm import Session
import time
import GPUtil

from shared.celery_app import celery_app
from shared.db.session import SessionLocal
from .services.memory_service import MemoryService
from .graph.build import build_graph, AgentState

# --- Worker起動時に一度だけ読み込む設定 ---
llm = ChatOllama(
    model="qwen2.5:32b-instruct",
    # model="deepseek-r1:671b",
    # model="deepseek-r1:70b",
    base_url="http://ollama:11434", temperature=0.0)

EMBEDDINGS = OllamaEmbeddings(model="mxbai-embed-large", base_url="http://ollama:11434")
CHROMA_KNOWLEDGE_PATH = "/app/worker/data/vectorstore_knowledge"
CHROMA_MEMORY_PATH = "/app/worker/data/vectorstore_memory"
vectorstore_knowledge = Chroma(persist_directory=CHROMA_KNOWLEDGE_PATH, embedding_function=EMBEDDINGS)
rag_retriever = vectorstore_knowledge.as_retriever(
    search_type="mmr",
    search_kwargs={'k': 10, 'fetch_k': 50}
)
vectorstore_memory = Chroma(persist_directory=CHROMA_MEMORY_PATH, embedding_function=EMBEDDINGS)

def wait_for_gpu(memory_threshold_mb=2000, interval=1, timeout=60):
    """
    指定した空きVRAM以上になるまで待機する関数
    """
    start_time = time.time()
    while True:
        gpus = GPUtil.getGPUs()
        if not gpus:
            # GPUが見つからなければ待たずに進む（CPU運用時など）
            break
        
        # 空きVRAMが閾値以上のGPUが1つでもあれば進む
        available = any(gpu.memoryFree > memory_threshold_mb for gpu in gpus)
        if available:
            break
        
        if time.time() - start_time > timeout:
            raise TimeoutError("GPUの空き待ちがタイムアウトしました。")
        
        time.sleep(interval)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@celery_app.task(name='worker.app.tasks.run_chat_graph')
def run_chat_graph(user_id: int, session_id: str, user_input: str) -> str:
    """
    AIの思考パイプラインを呼び出し、対話処理全体を管理するタスク。
    """
    # print(f"---TASK: GPU空き待機開始 (user_id: {user_id}, session_id: {session_id})---")
    # wait_for_gpu()
    # print(f"---TASK: GPU空き確保済み (user_id: {user_id}, session_id: {session_id})---")

    print(f"---TASK: 開始 (user_id: {user_id}, session_id: {session_id})---")
    final_response = "エラーにより応答を生成できませんでした。"
    with get_db() as db:
        memory_service = MemoryService(db_session=db, vectorstore_memory=vectorstore_memory)
        history_messages = memory_service.get_history(user_id=user_id, session_id=session_id)
        
        # build_graphに標準RAGのretrieverを渡す
        app = build_graph(rag_retriever=rag_retriever, llm=llm)

        # AgentStateの初期化
        initial_state = AgentState(
            user_input=user_input,
            history_messages=history_messages,
            intent="",
            expanded_queries=[],
            event_context="",
            knowledge_docs=[],
            realtime_schedule_info=None,
            final_response="",
            _retrieved_docs_metadata=[]
        )
        
        final_state = app.invoke(initial_state)
        final_response = final_state.get("final_response", final_response)
        
        print("---TASK: 会話を記憶に保存中---")
        last_turn_result = db.execute(
            text("SELECT MAX(turn) FROM conversation_history WHERE session_id = :session_id"),
            {"session_id": session_id}
        ).scalar()
        current_turn = (last_turn_result or 0) + 1

        memory_service.save_history(
            user_id=user_id,
            session_id=session_id,
            turn=current_turn,
            human_message=user_input,
            ai_message=final_response,
        )

    print(f"---TASK: 終了 (応答: {final_response})---")
    return final_response