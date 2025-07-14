# backend/worker/app/graph/build.py

import os
import re
from typing import TypedDict, Annotated, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

# 新しいパイプラインで利用するツールをインポート
from . import tools

# --- 1. グラフの状態 (AgentState) の拡張 ---
# 思考の過程でやり取りされる情報をすべて定義します。
class AgentState(TypedDict):
    # --- 初期入力 ---
    user_input: str
    history_messages: List[BaseMessage]

    # --- パイプラインの処理過程で生成・更新される情報 ---
    # 現在の状況 (BEFORE_EVENT, DURING_EVENT, AFTER_EVENT)
    event_context: str
    # RAGで取得した知識
    knowledge_docs: List[str]
    # リアルタイムのスケジュール情報 (任意)
    realtime_schedule_info: Optional[str]
    # 最終的なLLMの応答
    final_response: str
    # 回答に添える最終的なメッセージ (任意)
    final_addon_message: Optional[str]


# --- 2. グラフを構築する関数 ---
def build_graph(rag_retriever, llm):
    """
    コンテキスト認識型の思考パイプラインを構築します。
    """

    # --- 3. パイプラインの各ノード（ステップ）のロジックを定義 ---

    def contextualizer_node(state: AgentState):
        """【ノード1】状況判断: パイプラインの起点。イベントの状況を判断する。"""
        print("---GRAPH[1]: 状況を判断中---")
        context = tools.get_event_context()
        return {"event_context": context}

    def retrieve_knowledge_node(state: AgentState):
        """【ノード2】知識検索: ユーザーの質問と会話履歴から関連知識を検索する。"""
        print("---GRAPH[2]: 知識を検索中---")
        # 会話履歴と最新の質問を結合して、より文脈に沿った検索を行う
        contextual_question = "\n".join([msg.content for msg in state["history_messages"]]) + "\n" + state["user_input"]
        retrieved_docs = rag_retriever.invoke(contextual_question)
        
        # タイムテーブルJSONファイル自体が検索結果に含まれるのを防ぐ
        filtered_docs = [
            doc for doc in retrieved_docs if not doc.metadata.get("source", "").endswith(".json")
        ]

        doc_texts = [doc.page_content for doc in filtered_docs]
        return {"knowledge_docs": doc_texts}

    def conditional_augmentation_node(state: AgentState):
        """【ノード3】条件付き情報拡充: イベント当日のみリアルタイム情報を追加する。"""
        print(f"---GRAPH[3]: 条件付き情報拡充 (状況: {state['event_context']})---")
        if state["event_context"] == "DURING_EVENT":
            # ユーザーの質問から研究室名を抽出する（例: "山口研", "朴研"など）
            # ここでは正規表現で簡易的に抽出
            match = re.search(r"(.+研)", state["user_input"])
            lab_name = match.group(1) if match else None

            if lab_name:
                # 注意: timetable_pathの構築ロジックは実際のディレクトリ構造に合わせる必要があります
                # 例: .../経営システム工学科/研究室/サイバーフィジカルシステム研究室_山口研/timetable_yamaguchi_lab.json
                # このパスを動的に見つけるか、マッピングを持つ必要があります。
                # ここでは簡易的に、抽出した研究室名からファイルパスを推測します。
                # 実際には、より堅牢な方法（例: RAGで取得したドキュメントのメタデータからパスを取得）を検討します。
                # 今回はデモとして、山口研に決め打ちします。
                if "山口" in lab_name:
                    timetable_path = os.path.join(
                        tools.KNOWLEDGE_BASE_PATH,
                        "03_学部学科/システム科学技術学部/05_経営システム工学科/研究室/サイバーフィジカルシステム研究室_山口研/timetable_yamaguchi_lab.json"
                    )
                    schedule_info = tools.get_current_schedule_info(timetable_path)
                    return {"realtime_schedule_info": schedule_info}
        
        return {"realtime_schedule_info": None}


    def generate_response_node(state: AgentState):
        """【ノード4】応答生成: 全ての情報を元にLLMが回答を生成する。"""
        print("---GRAPH[4]: LLMで応答を生成中---")
        
        # LLMに渡す参考情報を組み立てる
        reference_info = "\n".join(state["knowledge_docs"])
        if state.get("realtime_schedule_info"):
            reference_info += "\n\n【リアルタイム情報】\n" + state["realtime_schedule_info"]

        system_prompt = (
            "あなたは秋田県立大学オープンキャンパスの、親切で優秀なAIアシスタントです。"
            "提供された会話履歴と以下の参考情報を元に、ユーザーの質問に日本語で自然に回答してください。\n\n"
            "【参考情報】:\n"
            f"{reference_info}"
        )
        
        # 過去の会話履歴と、ユーザーの最新の質問を結合
        messages = state["history_messages"] + [("human", state["user_input"])]
        prompt_messages = [("system", system_prompt)] + messages
        
        response = llm.invoke(prompt_messages)
        return {"final_response": response.content}

    def final_touch_node(state: AgentState):
        """【ノード5】最終調整: イベント前の場合のみ、特別なメッセージを末尾に追加する。"""
        print(f"---GRAPH[5]: 最終調整 (状況: {state['event_context']})---")
        if state["event_context"] == "BEFORE_EVENT":
            addon_message = tools.get_days_until_event_message()
            # 既存の応答にメッセージを追記
            final_response_with_addon = state["final_response"] + "\n\n" + addon_message
            return {"final_response": final_response_with_addon}
        
        # それ以外の状況では何もしない
        return {"final_response": state["final_response"]}


    # --- 4. グラフの組み立てと配線 ---
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
