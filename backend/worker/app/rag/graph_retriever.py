# backend/worker/app/rag/graph_retriever.py

import os
import json
import spacy
from neo4j import GraphDatabase
import logging

# --- ロギング設定 ---
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# --- Neo4j設定 ---
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"

# SpaCy日本語モデルのロード（tasks.pyと同じように起動時に一度だけ実行されるようにする）
# workerコンテナでja_core_news_smがダウンロード済みであることを前提
try:
    nlp = spacy.load("ja_core_news_sm")
except OSError:
    logging.error("SpaCy 'ja_core_news_sm' モデルが見つかりません。コンテナビルド中にインストールされているか確認してください。")
    # モデルがない場合は、関数が実行されないようにするか、適切なフォールバックを考慮
    nlp = None

# Neo4jドライバーの初期化（モジュールレベルで一度だけ）
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    driver.verify_connectivity()
    logging.info("Neo4jドライバーが正常に初期化されました。")
except Exception as e:
    logging.error(f"Neo4jへの接続に失敗しました: {e}")
    driver = None # 接続失敗時はドライバーをNoneに設定


def get_graph_context(query: str) -> str:
    """
    ユーザーのクエリを元に知識グラフから情報を検索し、LLMに渡すテキスト形式で返す。
    """
    if not driver:
        logging.error("Neo4jドライバーが利用できません。グラフ検索をスキップします。")
        return "（グラフ情報なし：Neo4j接続エラー）"

    extracted_keywords = []
    if nlp:
        doc = nlp(query)
        extracted_keywords = [chunk.text for chunk in doc.noun_chunks]
    logging.info(f"クエリから抽出されたキーワード: {extracted_keywords}")

    graph_context_parts = []
    with driver.session() as session:
        # ★★★ 修正: Cypherクエリを汎用化し、キーワードで動的にフィルタリング ★★★
        # まず、すべてのLabとExhibitionの関係を検索
        cypher_query_base = """
        MATCH (lab:Lab)-[:HAS_EXHIBITION|HAS_SCHEDULED_EXHIBITION]->(exhibition:Exhibition)
        OPTIONAL MATCH (exhibition)-[:HAS_PRESENTER|SCHEDULED_PRESENTER]->(presenter:Person)
        """

        # キーワードに基づいてWHERE句を動的に構築
        where_clauses = []
        if extracted_keywords:
            # 各キーワードがlab.name, exhibition.name, exhibition.descriptionのいずれかに含まれるかをチェック
            for keyword in extracted_keywords:
                # 部分一致検索を考慮し、正規表現またはCONTAINSを使用
                # CONTAINSは大文字小文字を区別するため、ToLower()で統一
                where_clauses.append(
                    f"(toLower(lab.name) CONTAINS toLower('{keyword}') OR "
                    f"toLower(exhibition.name) CONTAINS toLower('{keyword}') OR "
                    f"toLower(exhibition.description) CONTAINS toLower('{keyword}'))"
                )

        cypher_query = cypher_query_base
        if where_clauses:
            cypher_query += " WHERE " + " OR ".join(where_clauses) # 複数のキーワードはORで結合

        cypher_query += """
        WITH DISTINCT exhibition, lab, COLLECT(DISTINCT presenter.name) AS presenter_names,
             COLLECT(DISTINCT exhibition.start_time) AS start_times,
             COLLECT(DISTINCT exhibition.end_time) AS end_times,
             COLLECT(DISTINCT exhibition.location) AS locations
        RETURN 
            exhibition.name AS event_name, 
            exhibition.description AS event_description, 
            exhibition.full_content AS detail_content,
            presenter_names,
            start_times,
            end_times,        
            locations       
        ORDER BY event_name
        LIMIT 10
        """

        logging.info(f"  Executing Cypher Query:\n{cypher_query}")

        try:
            result = session.run(cypher_query)
            records_count = 0
            for record in result:
                records_count += 1
                logging.info(f"  Cypher Query Result Record: {record.data()}")

                event_name = record.get("event_name")
                event_desc = record.get("event_description") 
                presenter_names = record.get("presenter_names", []) 
                presenter_str = ", ".join(p for p in presenter_names if p) if presenter_names else "担当者不明"

                start_times = record.get("start_times", [])
                end_times = record.get("end_times", [])
                locations = record.get("locations", [])

                time_str = ""
                if start_times and end_times:
                    time_slots = []
                    for s, e in zip(start_times, end_times):
                        if s and e: time_slots.append(f"{s}〜{e}")
                    time_str = ", ".join(time_slots) if time_slots else "時間不明"

                location_str = ", ".join(l for l in locations if l) if locations else "場所不明"

                formatted_info = f"イベント名: {event_name if event_name else '不明なイベント名'}"
                if event_desc: 
                    formatted_info += f"\n説明: {event_desc}"
                formatted_info += f"\n担当: {presenter_str}"
                if time_str: formatted_info += f"\n時間: {time_str}"
                if location_str: formatted_info += f"\n場所: {location_str}"

                graph_context_parts.append(formatted_info)

            if not graph_context_parts: 
                logging.info("  Cypher Query returned no relevant records.")
                graph_context_parts.append("申し訳ありませんが、ご質問の出展情報はグラフから見つかりませんでした。") # メッセージを汎用化
            else:
                logging.info(f"  Cypher Query returned {records_count} unique records.")

        except Exception as e:
            logging.error(f"Cypherクエリ実行中にエラーが発生しました: {e}")
            graph_context_parts.append("グラフ検索中にエラーが発生しました。")

    final_graph_context_str = "\n\n".join(graph_context_parts)
    logging.info(f"--- Final Graph Context to LLM ---\n{final_graph_context_str}\n--- END Final Graph Context ---")
    return final_graph_context_str

    # ★★★ 追加: get_graph_contextが返す最終的な文字列をログに出力 ★★★
    final_graph_context_str = "\n\n".join(graph_context_parts)
    logging.info(f"--- Final Graph Context to LLM ---\n{final_graph_context_str}\n--- END Final Graph Context ---")
    return final_graph_context_str