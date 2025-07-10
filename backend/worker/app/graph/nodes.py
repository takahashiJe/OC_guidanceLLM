# backend/worker/app/graph/nodes.py

from backend.shared.state import AgentState

def retrieve_knowledge_node(state: AgentState, retriever):
    """
    ノード1: 知識の検索 (RAG)
    """
    print("---GRAPH: RAGで知識を検索中---")
    retrieved_docs = retriever.invoke(state["user_input"])
    doc_texts = [doc.page_content for doc in retrieved_docs]
    return {"knowledge_docs": doc_texts}

def generate_response_node(state: AgentState, llm):
    """
    ノード2: 応答生成
    """
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
