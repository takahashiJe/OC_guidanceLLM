# backend/worker/app/graph/build.py

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
# worker配下に移動したMemoryServiceをインポート
from ..services.memory_service import MemoryService
from shared.db.session import SessionLocal

# --- 1. グラフの状態を拡張 ---
class AgentState(TypedDict):
    # グラフ実行に必要な初期情報
    user_id: int
    session_id: str
    user_input: str
    # グラフの処理過程で生成されるデータ
    messages: Annotated[list, lambda x, y: x + y]
    knowledge_docs: List[str]
    llm_response: str


# --- 2. グラフを構築する関数 ---
def build_graph(rag_retriever, llm, vectorstore_memory):
    """
    記憶の取得から応答生成まで、一連の思考プロセスを内包したグラフを構築します。
    """
    # --- 3. グラフの各ノード（ステップ）のロジックを定義 ---

    def get_memory_node(state: AgentState):
        """ノード0: 記憶の取得"""
        print("---GRAPH: 記憶を取得中---")
        db = SessionLocal()
        try:
            # MemoryServiceはノード内でインスタンス化
            memory_service = MemoryService(db_session=db, vectorstore_memory=vectorstore_memory)
            history_messages = memory_service.get_history(
                user_id=state["user_id"],
                session_id=state["session_id"],
                latest_input=state["user_input"],
            )
        finally:
            db.close()
        
        # 取得した履歴と現在のユーザー入力を結合してmessagesに設定
        return {"messages": history_messages + [("human", state["user_input"])]}

    def retrieve_knowledge_node(state: AgentState):
        """ノード1: 知識の検索 (RAG)"""
        print("---GRAPH: RAGで知識を検索中---")
        # user_inputの代わりに、最新のメッセージ（ユーザー入力）を使うように変更
        latest_message = state["messages"][-1][1]
        retrieved_docs = rag_retriever.invoke(latest_message)
        doc_texts = [doc.page_content for doc in retrieved_docs]
        return {"knowledge_docs": doc_texts}

    def generate_response_node(state: AgentState):
        """ノード2: 応答生成"""
        print("---GRAPH: LLMで応答を生成中---")
        system_prompt = (
            "あなたは大学のオープンキャンパスを案内する親切なAIアシスタントです。"
            "提供された会話履歴と参考情報を元に、ユーザーの質問に日本語で回答してください。\n\n"
            "【参考情報】:\n"
            f"{state['knowledge_docs']}"
        )
        prompt_messages = [("system", system_prompt)] + state["messages"]
        response = llm.invoke(prompt_messages)
        return {"llm_response": response.content}


    # --- 4. グラフの組み立て ---
    graph = StateGraph(AgentState)

    graph.add_node("get_memory", get_memory_node)
    graph.add_node("retrieve_knowledge", retrieve_knowledge_node)
    graph.add_node("generate_response", generate_response_node)

    # エントリーポイントを記憶取得ノードに変更
    graph.set_entry_point("get_memory")
    graph.add_edge("get_memory", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()