# backend/worker/app/graph/build.py

import os
import re
from typing import TypedDict, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from . import tools

# AgentStateに、RAGが取得したファイルのメタデータを保持するフィールドを追加
class AgentState(TypedDict):
    user_input: str
    history_messages: List[BaseMessage]
    event_context: str
    knowledge_docs: List[str]
    realtime_schedule_info: Optional[str]
    final_response: str
    # ★ RAGが取得したドキュメントのメタデータ（ファイルパスなど）を保持する
    _retrieved_docs_metadata: List[dict] 

def build_graph(rag_retriever, llm):
    """
    コンテキスト認識型の思考パイプラインを構築します。
    """

    def contextualizer_node(state: AgentState):
        """【ノード1】状況判断"""
        print("---GRAPH[1]: 状況を判断中---")
        context = tools.get_event_context()
        return {"event_context": context}

    def retrieve_knowledge_node(state: AgentState):
        """【ノード2】知識検索: ファイルの中身とメタデータ（ファイルパス）の両方を取得"""
        print("---GRAPH[2]: 知識を検索中---")
        contextual_question = "\n".join([msg.content for msg in state["history_messages"]]) + "\n" + state["user_input"]
        retrieved_docs = rag_retriever.invoke(contextual_question)
        
        filtered_docs = [doc for doc in retrieved_docs if not doc.metadata.get("source", "").endswith(".json")]
        doc_texts = [doc.page_content for doc in filtered_docs]
        
        # ★ 取得したドキュメントのメタデータをstateに保存
        return {
            "knowledge_docs": doc_texts,
            "_retrieved_docs_metadata": [doc.metadata for doc in filtered_docs]
        }

    def conditional_augmentation_node(state: AgentState):
        """【ノード3】条件付き情報拡充: RAGが参照したファイルに応じてタイムテーブルを切り替える"""
        print(f"---GRAPH[3]: 条件付き情報拡充 (状況: {state['event_context']})---")
        
        if state["event_context"] != "DURING_EVENT":
            return {"realtime_schedule_info": None}

        retrieved_sources = [metadata.get("source", "") for metadata in state.get("_retrieved_docs_metadata", [])]
        schedule_info = None
        
        # --- ★ ここからが新しい判断ロジック ---
        
        # 1. 最優先：山口研のファイルが参照されたか？
        for source in retrieved_sources:
            if "サイバーフィジカルシステム研究室_山口研" in source:
                print("-> 山口研のタイムテーブルを参照します。")
                timetable_path = os.path.join(os.path.dirname(source), "timetable_yamaguchi_lab.json")
                schedule_info = tools.get_current_schedule_info(timetable_path)
                return {"realtime_schedule_info": schedule_info}
        
        # 2. 中優先：経営システム工学科のファイルが参照されたか？
        for source in retrieved_sources:
            if "05_経営システム工学科" in source:
                print("-> 経営システム工学科のタイムテーブルを参照します。（現在は未実装）")
                # (もし学科全体のタイムテーブルがあれば、ここでパスを指定)
                # timetable_path = os.path.join(...)
                # schedule_info = tools.get_current_schedule_info(timetable_path)
                # return {"realtime_schedule_info": schedule_info}
                pass # 現状はファイルがないので何もしない

        # 3. 通常：イベント概要のファイルが参照されたか？
        for source in retrieved_sources:
            if "00_イベント概要" in source:
                print("-> メインのタイムテーブルを参照します。")
                # timetable_main_event.jsonは00_イベント概要ディレクトリにあると仮定
                timetable_path = os.path.join(tools.KNOWLEDGE_BASE_PATH, "00_イベント概要", "timetable_main_event.json")
                schedule_info = tools.get_current_schedule_info(timetable_path)
                return {"realtime_schedule_info": schedule_info}

        return {"realtime_schedule_info": None}


    def generate_response_node(state: AgentState):
        """【ノード4】応答生成"""
        print("---GRAPH[4]: LLMで応答を生成中---")
        reference_info = "\n".join(state["knowledge_docs"])
        if state.get("realtime_schedule_info"):
            reference_info += "\n\n【リアルタイム情報】\n" + state["realtime_schedule_info"]

        system_prompt = (
            "あなたは秋田県立大学オープンキャンパスの、親切で優秀なAIアシスタントです。"
            "提供された会話履歴と以下の参考情報を元に、ユーザーの質問に日本語で自然に回答してください。\n\n"
            "【参考情報】:\n"
            f"{reference_info}"
        )
        
        messages = state["history_messages"] + [("human", state["user_input"])]
        prompt_messages = [("system", system_prompt)] + messages
        
        response = llm.invoke(prompt_messages)
        return {"final_response": response.content}

    def final_touch_node(state: AgentState):
        """【ノード5】最終調整"""
        print(f"---GRAPH[5]: 最終調整 (状況: {state['event_context']})---")
        if state["event_context"] == "BEFORE_EVENT":
            addon_message = tools.get_days_until_event_message()
            if addon_message:
                final_response_with_addon = state["final_response"] + "\n\n" + addon_message
                return {"final_response": final_response_with_addon}
        
        return {"final_response": state["final_response"]}

    # --- グラフの組み立てと配線 (変更なし) ---
    graph = StateGraph(AgentState)
    graph.add_node("contextualizer", contextualizer_node)
    graph.add_node("retrieve_knowledge", retrieve_knowledge_node)
    graph.add_node("conditional_augmentation", conditional_augmentation_node)
    graph.add_node("generate_response", generate_response_node)
    graph.add_node("final_touch", final_touch_node)
    graph.set_entry_point("contextualizer")
    graph.add_edge("contextualizer", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "conditional_augmentation")
    graph.add_edge("conditional_augmentation", "generate_response")
    graph.add_edge("generate_response", "final_touch")
    graph.add_edge("final_touch", END)

    return graph.compile()
