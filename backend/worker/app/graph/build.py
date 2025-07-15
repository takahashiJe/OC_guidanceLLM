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

    def retrieve_knowledge_node(state: AgentState):
        """【ノード2】知識検索: ユーザーの質問と会話履歴からグラフ情報を検索する。"""
        print("---GRAPH[2]: 知識を検索中 (グラフRAG)---")
        contextual_question = "\n".join([msg.content for msg in state["history_messages"]]) + "\n" + state["user_input"]

        # ★ グラフリトリーバーを呼び出す
        graph_info = graph_retriever(contextual_question) # get_graph_context を呼び出し

        # knowledge_docs は空のままでも良いし、必要なら他の情報（例: 汎用情報）をここに入れる
        return {"graph_context_info": graph_info, "knowledge_docs": []} # グラフ情報を状態にセット

    def conditional_augmentation_node(state: AgentState):
        """【ノード3】条件付き情報拡充: 現在はGraphRAGに集中するため、シンプル化または一時無効化を推奨"""
        print(f"---GRAPH[3]: 条件付き情報拡充 (状況: {state['event_context']})---")
        # GraphRAG実装中は、このノードのロジックは一旦シンプルにするか、
        # `timetable_yamaguchi_lab.json`からの詳細情報をget_graph_contextで取得するようにします。
        # 例外的なリアルタイム情報が必要な場合のみ有効に。
        # 現状は、`get_graph_context`で全てまかなう想定なので、ここでは何もしないことも可能です。
        return {"realtime_schedule_info": None} # または、既存のロジックを必要に応じて修正


    def generate_response_node(state: AgentState):
        """【ノード4】応答生成"""
        print("---GRAPH[4]: LLMで応答を生成中---")

        # LLMに渡す参考情報を組み立てる (グラフ情報を優先)
        reference_info_parts = []
        if state.get("graph_context_info"):
            # graph_context_info は既に '\n\n' で結合された formatted_info のリストになっている
            # これをさらに箇条書きに整形し、各出展情報を明確にする
            formatted_exhibits_list = []
            indent_replacement = '\n'
            for i, exhibit_info_str in enumerate(state["graph_context_info"].split('\n\n')):
                if exhibit_info_str.strip(): # 空でないことを確認
                    indented_exhibit_info = exhibit_info_str.replace('\n', indent_replacement)
                    formatted_exhibits_list.append(f"  {i+1}. {indented_exhibit_info}") 

            if formatted_exhibits_list:
                reference_info_parts.append("【グラフ情報 - 山口研の出展一覧】:\n" + "\n".join(formatted_exhibits_list))
            else:
                # グラフ情報が空の場合の明確な記述
                reference_info_parts.append("【グラフ情報 - 山口研の出展一覧】: （具体的な出展情報はグラフから見つかりませんでした。）")

        # もしChromaDBのRAGも併用するなら、knowledge_docsもここに加える
        # if state.get("knowledge_docs"):
        #    reference_info_parts.extend(state["knowledge_docs"]) 

        # realtime_schedule_info も必要に応じて追加
        # if state.get("realtime_schedule_info"):
        #    reference_info_parts.append(f"【リアルタイム情報】:\n{state['realtime_schedule_info']}")

        reference_info = "\n\n".join(reference_info_parts)

        # ★ システムプロンプトをグラフ情報に特化して修正
        system_prompt = (
            "あなたは秋田県立大学オープンキャンパスの、親切で優秀なAIアシスタントです。\n"
            "提供された会話履歴と以下の【参考情報】を元に、ユーザーの質問に日本語で自然に回答してください。\n"
            "\n"
            "**【最重要ルール：厳守してください！】**\n"
            "1.  **回答の根拠は必ず【グラフ情報 - 山口研の出展一覧】セクションの情報のみ**にしてください。\n"
            "2.  **出展一覧に記載されていない内容は、絶対に回答に含めないでください。**\n"
            "3.  **もし【グラフ情報 - 山口研の出展一覧】が「具体的な出展情報はグラフから見つかりませんでした。」と記載されている場合、**\n"
            "    **必ず「申し訳ありませんが、山口研究室の具体的な出展情報は現在確認できません。」と回答してください。**\n"
            "4.  **提供された出展一覧の全ての項目を、分かりやすい箇条書き形式で提示してください。**\n"
            "5.  **イベント名、説明、担当、時間、場所の各項目を明確に示してください。**\n"
            "6.  **「他の研究室や部門に関連する」というような、事実と異なる憶測は絶対にしないでください。**\n"
            "7.  **会話履歴は、回答の文脈を理解するためにのみ使用し、回答内容に直接含めないでください。**\n"
            "\n"
            "【参考情報】:\n"
            f"{reference_info}"
            )

        print("\n---DEBUG: Full System Prompt sent to LLM ---")
        print(system_prompt)
        print("---END DEBUG: Full System Prompt---")
        
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
