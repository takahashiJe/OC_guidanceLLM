# backend/worker/app/graph/build.py

import os
import re
from typing import TypedDict, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langchain_core.pydantic_v1 import BaseModel, Field

from . import tools

class Intent(BaseModel):
    """ユーザーの入力の意図を分類する。"""
    intent: Literal["knowledge_question", "chitchat", "greeting"] = Field(
        description="ユーザーの入力の意図。'knowledge_question'は情報検索が必要な質問、'chitchat'は雑談、'greeting'は挨拶。",
        default="chitchat"
    )

# AgentStateに、RAGが取得したファイルのメタデータを保持するフィールドを追加
class AgentState(TypedDict):
    user_input: str
    history_messages: List[BaseMessage]
    intent: str
    expanded_query: str  # ★ 新しく追加: 拡張された検索クエリ
    event_context: str
    knowledge_docs: List[str] # 必要に応じてGraphRAGからのテキスト情報もここにまとめる
    realtime_schedule_info: Optional[str]
    final_response: str
    _retrieved_docs_metadata: List[dict] # 必要に応じて、GraphRAGでもメタデータを追跡可能
    graph_context_info: Optional[str] # ★ 新しいグラフ情報フィールド

def build_graph(graph_retriever, llm):
    """
    コンテキスト認識型の思考パイプラインを構築します。
    """

    def contextualizer_node(state: AgentState):
        """【ノード1】状況判断"""
        print("---GRAPH[1]: 状況を判断中---")
        context = tools.get_event_context()
        return {"event_context": context}
    
    def classify_intent_node(state: AgentState):
        """【ノード2】意図分類: ユーザーの入力が質問か雑談かを判断"""
        print("---GRAPH[2]: ユーザーの意図を分類中---")
        
        prompt = f"""以下のユーザーの最後の発言を分析し、その意図を分類してください。
        - 情報を求めている具体的な質問は 'knowledge_question'
        - 単純な挨拶（こんにちは、など）は 'greeting'
        - 上記以外（ありがとう、すごい、など）は 'chitchat'
        
        ユーザーの発言: "{state['user_input']}"
        """
        
        # 構造化LLMを呼び出して意図を分類
        response = structured_llm.invoke([("human", prompt)])
        intent = response.intent
        print(f"  - 分類結果: {intent}")
        return {"intent": intent}

    def query_expansion_node(state: AgentState):
        """【ノード3-A】クエリー拡張: 履歴を元に検索クエリを生成 (RAGパス)"""
        print("---GRAPH[3-A]: 検索クエリを拡張中---")
        history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in state["history_messages"]])
        prompt = f"""以下の会話履歴と最後の質問を考慮して、ベクトルデータベースで関連情報を検索するための、自己完結した最適な検索クエリを生成してください。
        検索クエリは、秋田県立大学のオープンキャンパスに関する情報を検索するものであるべきです。

        【会話履歴】
        {history_str}

        【最後の質問】
        {state['user_input']}

        【生成する検索クエリ】"""
        query_generation_messages = [
            SystemMessage(content="あなたは、ユーザーの質問を解析し、ベクトル検索に最適なクエリを生成する優秀なアシスタントです。"),
            ("human", prompt)
        ]
        response = llm.invoke(query_generation_messages)
        expanded_query = response.content.strip()
        print(f"  - 生成されたクエリ: {expanded_query}")
        return {"expanded_query": expanded_query}
    
    def query_expansion_node(state: AgentState):
        """【ノード2】クエリー拡張: 履歴を元に検索クエリを生成"""
        print("---GRAPH[2]: 検索クエリを拡張中---")

        history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in state["history_messages"]])
        
        # LLMにクエリ生成を依頼する
        prompt = f"""以下の会話履歴と最後の質問を考慮して、ベクトルデータベースで関連情報を検索するための、自己完結した最適な検索クエリを生成してください。
        検索クエリは、秋田県立大学のオープンキャンパスに関する情報を検索するものであるべきです。

        【会話履歴】
        {history_str}

        【最後の質問】
        {state['user_input']}

        【生成する検索クエリ】"""

        query_generation_messages = [
            SystemMessage(content="あなたは、ユーザーの質問を解析し、ベクトル検索に最適なクエリを生成する優秀なアシスタントです。"),
            ("human", prompt)
        ]
        
        response = llm.invoke(query_generation_messages)
        expanded_query = response.content.strip()
        
        print(f"  - 生成されたクエリ: {expanded_query}")
        return {"expanded_query": expanded_query}

    def retrieve_knowledge_node(state: AgentState):
        """【ノード3】知識検索: 拡張されたクエリでベクトルDBを検索"""
        print("---GRAPH[3]: 知識を検索中 (標準RAG)---")
        
        # 拡張されたクエリを使用
        expanded_query = state["expanded_query"]
        retrieved_docs = rag_retriever.invoke(expanded_query)

        # 取得したドキュメントの内容とメタデータをstateに保存
        knowledge_docs = [doc.page_content for doc in retrieved_docs]
        metadata_list = [doc.metadata for doc in retrieved_docs]
        
        print(f"  - {len(knowledge_docs)}件のドキュメントを取得しました。")
        return {"knowledge_docs": knowledge_docs, "_retrieved_docs_metadata": metadata_list}

    def conditional_augmentation_node(state: AgentState):
        """【ノード5-A】条件付き情報拡充 (RAGパス)"""
        print(f"---GRAPH[5-A]: 条件付き情報拡充 (状況: {state['event_context']})---")
        return {"realtime_schedule_info": None}


    def generate_rag_response_node(state: AgentState):
        """【ノード6-A】応答生成 (RAGパス)"""
        print("---GRAPH[6-A]: RAG応答を生成中---")
        reference_info_parts = []
        if state.get("knowledge_docs"):
            doc_strings = []
            for i, (doc, meta) in enumerate(zip(state["knowledge_docs"], state["_retrieved_docs_metadata"])):
                source = meta.get('source', '不明なソース')
                doc_strings.append(f"[{i+1}] ソース: {os.path.basename(source)}\n内容: {doc}")
            reference_info_parts.append("【参考情報】:\n" + "\n\n".join(doc_strings))
        
        if state.get("realtime_schedule_info"):
            reference_info_parts.append(f"【リアルタイム情報】:\n{state['realtime_schedule_info']}")

        reference_info = "\n\n".join(reference_info_parts)
        system_prompt = (
            "あなたは秋田県立大学オープンキャンパスの、親切で優秀なAIアシスタントです。\n"
            "提供された会話履歴と以下の【参考情報】を元に、ユーザーの質問に日本語で自然に回答してください。\n"
            "**回答には、どの【参考情報】のどの部分を根拠にしたか、番号で `[1]` のように示してください。**\n"
            "もし参考情報の中に回答の根拠となる情報が見つからない場合は、無理に回答を生成せず、「申し訳ありませんが、その質問に関する情報は現在持ち合わせておりません。」と正直に回答してください。\n\n"
            f"{reference_info}"
        )
        messages = state["history_messages"] + [("human", state["user_input"])]
        prompt_messages = [("system", system_prompt)] + messages
        response = llm.invoke(prompt_messages)
        return {"final_response": response.content}
    
    def handle_chitchat_node(state: AgentState):
        """【ノード3-B】雑談応答 (雑談パス)"""
        print("---GRAPH[3-B]: 雑談応答を生成中---")
        intent = state.get("intent")
        if intent == "greeting":
            response = "こんにちは！秋田県立大学オープンキャンパスAIアシスタントです。何かお手伝いできることはありますか？"
        else: # chitchat
            response = "はい、ありがとうございます。他にご質問はありますか？"
        return {"final_response": response}

    def final_touch_node(state: AgentState):
        """【ノード5】最終調整"""
        print(f"---GRAPH[5]: 最終調整 (状況: {state['event_context']})---")
        if state["event_context"] == "BEFORE_EVENT":
            addon_message = tools.get_days_until_event_message()
            if addon_message:
                final_response_with_addon = state["final_response"] + "\n\n" + addon_message
                return {"final_response": final_response_with_addon}
        
        return {"final_response": state["final_response"]}

    # --- 条件分岐ロジック ---
    def route_after_classification(state: AgentState):
        """意図分類の結果に応じて、次のノードを決定する"""
        intent = state.get("intent")
        if intent == "knowledge_question":
            return "query_expansion"
        else: # greeting, chitchat
            return "handle_chitchat"

    # --- グラフの組み立てと配線 ---
    graph = StateGraph(AgentState)
    
    # ノードの追加
    graph.add_node("contextualizer", contextualizer_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("query_expansion", query_expansion_node)
    graph.add_node("retrieve_knowledge", retrieve_knowledge_node)
    graph.add_node("conditional_augmentation", conditional_augmentation_node)
    graph.add_node("generate_rag_response", generate_rag_response_node)
    graph.add_node("handle_chitchat", handle_chitchat_node)
    graph.add_node("final_touch", final_touch_node)

    # パイプラインの配線
    graph.set_entry_point("contextualizer")
    graph.add_edge("contextualizer", "classify_intent")

    # ★★★ 意図分類後の条件分岐 ★★★
    graph.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "query_expansion": "query_expansion",
            "handle_chitchat": "handle_chitchat"
        }
    )

    # RAGパスの配線
    graph.add_edge("query_expansion", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "conditional_augmentation")
    graph.add_edge("conditional_augmentation", "generate_rag_response")
    graph.add_edge("generate_rag_response", "final_touch")

    # 雑談パスの配線
    graph.add_edge("handle_chitchat", "final_touch")
    
    # 最終調整ノードから終了
    graph.add_edge("final_touch", END)

    return graph.compile()