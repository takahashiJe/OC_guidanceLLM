# backend/worker/app/graph/build.py

import os
from typing import TypedDict, List, Optional, Literal

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END

from . import tools

# --- Pydanticモデル定義 ---

class Intent(BaseModel):
    """ユーザーの入力の意図を分類する。"""
    intent: Literal["knowledge_question", "chitchat", "greeting"] = Field(
        description="ユーザーの入力の意図。'knowledge_question'は情報検索が必要な質問、'chitchat'は雑談、'greeting'は挨拶。",
        default="chitchat"
    )

class MultiQuery(BaseModel):
    """ユーザーの質問を分析し、複数の検索クエリを生成する。"""
    queries: List[str] = Field(
        description="生成された3〜5個の検索クエリのリスト。"
    )

# --- AgentState定義 ---
class AgentState(TypedDict):
    user_input: str
    history_messages: List[BaseMessage]
    intent: str
    expanded_queries: List[str]
    event_context: str
    knowledge_docs: List[str]
    realtime_schedule_info: Optional[str]
    final_response: str
    _retrieved_docs_metadata: List[dict]

def build_graph(rag_retriever, llm):
    """
    Multi-Query Expansionと詳細な知識インデックスを活用した、最高精度の思考パイプラインを構築します。
    """
    
    def contextualizer_node(state: AgentState):
        """【ノード1】状況判断"""
        print("---GRAPH[1]: 状況を判断中---")
        context = tools.get_event_context()
        return {"event_context": context}

    def classify_intent_node(state: AgentState):
        """【ノード2】意図分類"""
        print("---GRAPH[2]: ユーザーの意図を分類中---")
        json_parser = JsonOutputParser(pydantic_object=Intent)
        prompt = f"""以下のユーザーの最後の発言を分析し、その意図を分類してください。
        - 情報を求めている具体的な質問は 'knowledge_question'
        - 単純な挨拶（こんにちは、など）は 'greeting'
        - 上記以外（ありがとう、すごい、など）は 'chitchat'
        {json_parser.get_format_instructions()}
        ユーザーの発言: "{state['user_input']}"
        """
        chain = llm | json_parser
        response_json = chain.invoke([("human", prompt)])
        intent = response_json.get("intent", "chitchat")
        print(f"  - 分類結果: {intent}")
        return {"intent": intent}

    def query_expansion_node(state: AgentState):
        """【ノード3-A】複数クエリ生成"""
        print("---GRAPH[3-A]: 複数検索クエリを生成中---")
        
        json_parser = JsonOutputParser(pydantic_object=MultiQuery)
        history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in state["history_messages"]])

        # ★★★ ここから修正 ★★★
        # 利用可能なドキュメントの概要を、省略せずに詳細に記述
        knowledge_index = """
        - **イベント概要**:
        - オープンキャンパス基本情報、参加・予約方法、主なプログラム一覧、体験型模擬授業詳細
        - 保護者向け説明会、総合型選抜プレゼン講座、交通アクセスと無料送迎バス、無料昼食体験
        - **大学の概要**:
        - 理念とビジョン、歴史と学長メッセージ
        - **大学の特色**:
        - 少人数教育、学生自主研究制度、最先端の研究環境、地域連携と国際交流
        - **学部・学科**:
        - **システム科学技術学部**:
            - 学部概要
            - 機械工学科（概要）
            - 知能メカトロニクス学科（概要）
            - 情報工学科（概要）
            - 建築環境システム学科（概要）
            - **経営システム工学科**:
            - 学科概要
            - **研究室**:
                - サイバーフィジカルシステム研究室（山口研）: 研究室概要、オープンキャンパス出展内容
                - **出展詳細**:
                    - 吉田快: サーバーダッシュボード
                    - 佐藤翔真: ヒューマンタワーバトル
                    - 高橋潤大: APU-NaviAI
                    - 小川春翔: StoryClash
                    - 山根拓真: AIRhythmix
                    - 成田明音: GraffitiInMotion
                    - 新井美羽: SummonWeaponsAdventure
                    - 高橋夢叶: AutomatedWebsiteCreator
                - 先端ビジネス会計研究室（朴研）: 研究室概要
                - 応用経済研究室（嶋崎(善)研）: 研究室概要
                - 環境システム研究室（金澤研）: 研究室概要
                - 経営数理解析（星野研）: 研究室概要
        - **生物資源科学部**:
            - 応用生物科学科、生物生産科学科、生物環境科学科、アグリビジネス学科の概要
        - **キャンパスライフ**:
        - 年間行事、クラブ活動、施設紹介、学生寮「清新寮」
        - **学生支援**:
        - 奨学金と経済的支援、相談窓口とキャリア支援
        """

        prompt = f"""あなたは、ユーザーの質問を分析し、ベクトル検索のヒット率を最大化するために、多様な検索クエリを生成する専門家です。
        与えられた【利用可能なドキュメントの概要】を**最優先の参考情報**として、ユーザーの質問に答えられる情報がどのドキュメントにありそうか見当をつけ、最適な検索クエリを3〜5個生成してください。

        **クエリ生成の戦略:**
        1.  **書き換えクエリ**: ユーザーの質問を、概要にある言葉を使ってより具体的に書き換える。
        2.  **仮想文書クエリ**: 質問の答えがありそうな文書のタイトルや要約を、概要を参考にしつつ生成する。
        3.  **キーワードクエリ**: 概要に含まれる固有名詞や専門用語を抜き出す。

        **【最重要ルール】**
        - **必ず【利用可能なドキュメントの概要】に記載のある情報に基づいてクエリを生成してください。**
        - **概要にないトピック（例：入試の過去問、サークルの詳細な活動内容など）に関する質問が来た場合は、その旨を示すクエリを生成してください。**

        {json_parser.get_format_instructions()}

        ---
        【利用可能なドキュメントの概要】
        {knowledge_index}
        ---

        【会話履歴】
        {history_str if history_str else "なし"}

        【最後の質問】
        {state['user_input']}
        """
        # ★★★ ここまで修正 ★★★

        chain = llm | json_parser
        response_json = chain.invoke([("human", prompt)])
        
        queries = response_json.get("queries", [])
        print(f"  - 生成されたクエリリスト: {queries}")
        
        return {"expanded_queries": queries}

    def retrieve_knowledge_node(state: AgentState):
        """【ノード4-A】複数クエリでの知識検索と結果の統合"""
        print("---GRAPH[4-A]: 複数クエリで知識を検索中---")
        
        queries = state.get("expanded_queries", [])
        if not queries:
            print("  - 検索クエリがないため、検索をスキップします。")
            return {"knowledge_docs": [], "_retrieved_docs_metadata": []}

        all_retrieved_docs = []
        for query in queries:
            retrieved = rag_retriever.invoke(query)
            all_retrieved_docs.extend(retrieved)
            print(f"  - クエリ「{query[:30]}...」で {len(retrieved)} 件取得")

        unique_docs = {}
        for doc in all_retrieved_docs:
            unique_docs[doc.page_content] = doc
        
        final_docs = list(unique_docs.values())
        
        knowledge_docs = [doc.page_content for doc in final_docs]
        metadata_list = [doc.metadata for doc in final_docs]
        
        print(f"  - 重複排除後、合計 {len(final_docs)} 件のユニークなドキュメントを取得しました。")
        return {"knowledge_docs": knowledge_docs, "_retrieved_docs_metadata": metadata_list}

    def generate_rag_response_node(state: AgentState):
        """【ノード5-A】応答生成"""
        print("---GRAPH[5-A]: RAG応答を生成中---")
        reference_info_parts = []
        if state.get("knowledge_docs"):
            doc_strings = []
            for i, (doc, meta) in enumerate(zip(state["knowledge_docs"], state["_retrieved_docs_metadata"])):
                source = meta.get('source', '不明なソース')
                doc_strings.append(f"[{i+1}] ソース: {os.path.basename(source)}\n内容: {doc}")
            reference_info_parts.append("【参考情報】:\n" + "\n\n".join(doc_strings))
        
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
        """【ノード3-B】雑談応答"""
        print("---GRAPH[3-B]: 雑談応答を生成中---")
        intent = state.get("intent")
        if intent == "greeting":
            response = "こんにちは！秋田県立大学オープンキャンパスAIアシスタントです。何かお手伝いできることはありますか？"
        else:
            response = "はい、ありがとうございます。他にご質問はありますか？"
        return {"final_response": response}

    def final_touch_node(state: AgentState):
        """【最終ノード】最終調整"""
        print(f"---GRAPH[FINAL]: 最終調整 (状況: {state['event_context']})---")
        if state["event_context"] == "BEFORE_EVENT":
            addon_message = tools.get_days_until_event_message()
            if addon_message and state.get("intent") == "knowledge_question":
                final_response_with_addon = state["final_response"] + "\n\n" + addon_message
                return {"final_response": final_response_with_addon}
        return {"final_response": state["final_response"]}

    def route_after_classification(state: AgentState):
        """意図分類後のルーティング"""
        intent = state.get("intent")
        if intent == "knowledge_question":
            return "query_expansion"
        else:
            return "handle_chitchat"

    # --- グラフの組み立てと配線 ---
    graph = StateGraph(AgentState)
    
    graph.add_node("contextualizer", contextualizer_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("query_expansion", query_expansion_node)
    graph.add_node("retrieve_knowledge", retrieve_knowledge_node)
    graph.add_node("generate_rag_response", generate_rag_response_node)
    graph.add_node("handle_chitchat", handle_chitchat_node)
    graph.add_node("final_touch", final_touch_node)

    graph.set_entry_point("contextualizer")
    graph.add_edge("contextualizer", "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "query_expansion": "query_expansion",
            "handle_chitchat": "handle_chitchat"
        }
    )

    graph.add_edge("query_expansion", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "generate_rag_response")
    graph.add_edge("generate_rag_response", "final_touch")
    graph.add_edge("handle_chitchat", "final_touch")
    graph.add_edge("final_touch", END)

    return graph.compile()
