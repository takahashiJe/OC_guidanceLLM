# backend/worker/app/graph/build.py

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

# --- 1. グラフの状態を定義 ---
# 記憶の取得・保存に関するフィールドが不要になり、よりシンプルになる
class AgentState(TypedDict):
    user_input: str
    messages: Annotated[list, lambda x, y: x + y]
    knowledge_docs: List[str]
    llm_response: str


# --- 2. グラフを構築する関数 ---
def build_graph(rag_retriever, llm):
    """
    RAGとLLMを統合した、純粋な思考プロセスとしてのグラフを構築します。
    """

    # --- 3. グラフの各ノード（ステップ）のロジックを定義 ---

    def retrieve_knowledge_node(state: AgentState):
        """ノード1: 知識の検索 (RAG)"""
        print("---GRAPH: RAGで知識を検索中---")
        retrieved_docs = rag_retriever.invoke(state["user_input"])
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

    # ノードをグラフに追加
    graph.add_node("retrieve_knowledge", retrieve_knowledge_node)
    graph.add_node("generate_response", generate_response_node)

    # エッジ（処理の流れ）を定義
    graph.set_entry_point("retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "generate_response")
    graph.add_edge("generate_response", END) # 応答を生成したらグラフの役割は終了

    # グラフをコンパイルして返す
    return graph.compile()

