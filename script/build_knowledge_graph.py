# script/build_knowledge_graph.py

import os
import json
import spacy
import logging
from neo4j import GraphDatabase
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document # Documentクラスをインポート
import re
from typing import Any, List, Dict # List, Dict も追加

# --- ロギング設定 ---
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# --- Neo4j設定 ---
KNOWLEDGE_BASE_DIR = "backend/worker/data/knowledge"
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"

# SpaCy日本語モデルのロード
try:
    nlp = spacy.load("ja_core_news_sm")
except OSError:
    logging.error("SpaCy 'ja_core_news_sm' モデルが見つかりません。'python -m spacy download ja_core_news_sm' を実行してください。")
    exit(1)

# Neo4jドライバーの初期化
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# --- 修正: load_documents関数 ---
def load_documents(directory: str) -> List[Any]:
    """
    指定されたディレクトリからMarkdownおよびJSONドキュメントを読み込む。
    GraphRAGに必要な特定のファイルを対象とする。
    """
    all_docs = []

    specific_files = [
        os.path.join(directory, "03_学部学科/システム科学技術学部/05_経営システム工学科/研究室/サイバーフィジカルシステム研究室_山口研/01_研究室概要.md"),
        os.path.join(directory, "03_学部学科/システム科学技術学部/05_経営システム工学科/研究室/サイバーフィジカルシステム研究室_山口研/timetable_yamaguchi_lab.json")
    ]

    exhibit_details_dir = os.path.join(directory, "03_学部学科/システム科学技術学部/05_経営システム工学科/研究室/サイバーフィジカルシステム研究室_山口研/出展詳細")
    if os.path.exists(exhibit_details_dir):
        for file in os.listdir(exhibit_details_dir):
            if file.endswith(".md"):
                specific_files.append(os.path.join(exhibit_details_dir, file))

    logging.info(f"対象ドキュメントを読み込み中 ({len(specific_files)} ファイルを処理):")
    for file_path in specific_files:
        if not os.path.exists(file_path):
            logging.warning(f"ファイルが見つかりません: {file_path}")
            continue
        try:
            if file_path.endswith(".md"):
                # ★★★ ここを修正: ファイル全体を文字列として読み込む ★★★
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                doc = Document(page_content=raw_content, metadata={"source": file_path, "type": "md_full_file"})
                all_docs.append(doc)
                logging.info(f"  読み込み済み (MD FULL FILE): {file_path}")
            elif file_path.endswith(".json"):
                # JSONファイルは直接読み込み、page_contentを文字列として渡す
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()

                doc = Document(page_content=raw_content, metadata={"source": file_path, "type": "json_raw_string"})
                all_docs.append(doc)
                logging.info(f"  読み込み済み (JSON RAW STRING): {file_path}")
        except Exception as e:
            logging.error(f"ファイルの読み込み中にエラー: {file_path}, 詳細: {e}")

    logging.info(f"合計 {len(all_docs)} 個のドキュメントチャンクを読み込みました。")
    for i, doc in enumerate(all_docs):
        logging.info(f"  Doc {i}: Source='{doc.metadata.get('source', 'N/A')}', Type={type(doc.page_content)}")
        if isinstance(doc.page_content, str):
            logging.info(f"    Content (STRING HEAD): {doc.page_content[:200]}...")
        elif isinstance(doc.page_content, (list, dict)): # このパスは新しい読み込み方では発生しないはず
            logging.info(f"    Content (OBJECT HEAD): {str(doc.page_content)[:200]}...")
    return all_docs

# --- extract_entities_and_relations関数 (MDの正規表現も修正) ---
def extract_entities_and_relations(doc_page_content: Any, source_path: str) -> (List[Dict], List[Dict]):
    """
    ドキュメントの内容とソースパスからエンティティと関係性を抽出する。
    doc_page_contentは、MDの場合は文字列、JSONの場合は文字列。
    """
    entities = []
    relations = []
    lab_name_full = "サイバーフィジカルシステム研究室_山口研"

    entities.append({"name": lab_name_full, "label": "Lab", "source_path": source_path})

    logging.info(f"  --- Extracting from: {source_path} ---")

    # --- 研究室概要ファイル (01_研究室概要.md) の処理 ---
    if "01_研究室概要.md" in source_path:
        doc_content_str = str(doc_page_content)
        logging.info(f"  Type: 研究室概要MD")

        match = re.search(r"担当教員 \| (.+?)（", doc_content_str)
        if match:
            presenter_name = match.group(1).strip()
            entities.append({"name": presenter_name, "label": "Person", "source_path": source_path})
            relations.append({"start": lab_name_full, "end": presenter_name, "type": "HAS_HEAD_PROFESSOR", "properties": {"source": source_path}})

        vision_match = re.search(r"研究室のビジョン\| (.+?) \|", doc_content_str, re.DOTALL)
        if vision_match:
            vision_text = vision_match.group(1).strip()
            entities.append({"name": lab_name_full, "label": "Lab", "vision": vision_text, "source_path": source_path})

    # --- 各出展詳細Markdownファイルの処理 ---
    elif "出展詳細" in source_path and source_path.endswith(".md"):
        doc_content_str = str(doc_page_content)
        logging.info(f"  Type: 出展詳細MD")

        # プレゼンター名の抽出 (例: # 吉田 快（修士2年）: Server Management Dashboard)
        # 行頭の'# 'から、括弧（）の前の氏名部分をキャプチャ。その後ろに': 'と続くタイトルはオプション
        presenter_line_match = re.search(r"^#\s*([^（]+?)（.+?）(?:\s*:\s*(.+))?", doc_content_str, re.MULTILINE)
        presenter_name = presenter_line_match.group(1).strip() if presenter_line_match else "不明な担当者"

        # 出展テーマの抽出 (例: ## 出展テーマ：Server Management Dashboard)
        # 「## 出展テーマ：」の直後から改行までをキャプチャ
        theme_match = re.search(r"## 出展テーマ：([^\n]+)", doc_content_str)
        exhibition_theme = theme_match.group(1).strip() if theme_match else "不明な出展テーマ"

        # 短い説明の抽出 (例: ### 計算機のお熱、計ってみませんか？ AIの"仕事ぶり"をリアルタイムで可視化！)
        # 形式: ### キャッチフレーズ\n\n**メインの説明文**
        # 両方をキャプチャし、結合
        short_desc_match = re.search(r"###\s*([^\n]+)\n\n\*\*(.+?)\*\*", doc_content_str, re.DOTALL)
        short_description = ""
        if short_desc_match:
            short_description = f"{short_desc_match.group(1).strip()}\n\n{short_desc_match.group(2).strip()}"
        else:
            # 特定のパターンに合致しない場合（例: '**'がない場合）、最初の###行のみを抽出
            short_desc_fallback_match = re.search(r"###\s*([^\n]+)", doc_content_str)
            if short_desc_fallback_match:
                short_description = short_desc_fallback_match.group(1).strip()

        # エンティティの追加
        entities.append({"name": exhibition_theme, "label": "Exhibition", "description": short_description, "source_path": source_path, "full_content": doc_content_str})
        entities.append({"name": presenter_name, "label": "Person", "source_path": source_path})

        # 関係性の追加
        relations.append({"start": lab_name_full, "end": exhibition_theme, "type": "HAS_EXHIBITION", "properties": {"source": source_path}})
        relations.append({"start": exhibition_theme, "end": presenter_name, "type": "HAS_PRESENTER", "properties": {"source": source_path}})

        logging.info(f"    Extracted Exhibition: '{exhibition_theme}', Presenter: '{presenter_name}', ShortDesc: '{short_description[:50]}...'")

    # --- タイムテーブルJSON (timetable_yamaguchi_lab.json) の処理 ---
    elif "timetable_yamaguchi_lab.json" in source_path:
        logging.info(f"  Type: タイムテーブルJSON")

        timetable_data = None
        if isinstance(doc_page_content, str): # doc_page_contentが文字列であることを期待
            try:
                timetable_data = json.loads(doc_page_content)
                logging.info(f"    JSON string parsed successfully from {source_path}")
            except json.JSONDecodeError as e:
                logging.error(f"    JSON文字列の解析エラー: {source_path}, 詳細: {e}")
                return [], [] # 解析失敗時はエンティティ・関係性を返さない
        elif isinstance(doc_page_content, list): # 万が一既にリストの場合
            timetable_data = doc_page_content
            logging.info(f"    JSON is already a list from {source_path}")
        else:
            logging.error(f"    予期せぬJSONデータタイプ: {source_path}, Type: {type(doc_page_content)}")
            return [], [] # 予期せぬタイプの場合は処理をスキップ

        if not timetable_data: 
            logging.warning(f"    タイムテーブルデータが空または解析できませんでした: {source_path}")
            return [], []

        try:
            for entry in timetable_data:
                event_name = entry.get("event_name")
                description = entry.get("description")
                presenter = entry.get("presenter")
                start_time = entry.get("start_time")
                end_time = entry.get("end_time")
                location = entry.get("location")

                if event_name:
                    entity_props = {"name": event_name, "label": "Exhibition", "source_path": source_path}
                    if description: entity_props["description"] = description
                    if start_time: entity_props["start_time"] = start_time
                    if end_time: entity_props["end_time"] = end_time
                    if location: entity_props["location"] = location

                    entities.append(entity_props)
                    logging.info(f"    Extracted JSON Exhibition: '{event_name}', Props: {list(entity_props.keys())}, Values: {entity_props}")

                    relations.append({"start": lab_name_full, "end": event_name, "type": "HAS_SCHEDULED_EXHIBITION", "properties": {"source": source_path}})

                    if presenter:
                        entities.append({"name": presenter, "label": "Person", "source_path": source_path})
                        relations.append({"start": event_name, "end": presenter, "type": "SCHEDULED_PRESENTER", "properties": {"source": source_path}})
        except Exception as e:
            logging.error(f"タイムテーブルデータの処理エラー: {source_path}, 詳細: {e}")

    logging.info(f"  Extraction Result - Entities: {len(entities)}, Relations: {len(relations)}")
    return entities, relations

def create_graph_nodes_and_relations(entities, relations):
    """Neo4jにノードと関係を作成する"""
    with driver.session() as session:
        logging.info(f"--- Batch processing: Creating/Merging {len(entities)} Nodes and {len(relations)} Relationships ---")

        # 1. ノードの作成とプロパティ設定
        for ent in entities:
            try:
                session.run(f"MERGE (n:{ent['label']} {{name: $name}})", name=ent["name"])

                props_to_set = {k: v for k, v in ent.items() if k not in ["name", "label", "source_path"]}

                if props_to_set:
                    session.run(f"MATCH (n:{ent['label']} {{name: $name}}) SET n += $props", 
                                name=ent["name"], props=props_to_set)
                    logging.info(f"  MERGED Node: (:{ent['label']} {{name: '{ent['name']}'}}), SET Props: {list(props_to_set.keys())}, Values: {props_to_set}")
                else:
                    logging.info(f"  MERGED Node: (:{ent['label']} {{name: '{ent['name']}'}}), No additional props to set.")
            except Exception as e:
                logging.error(f"  Error creating/setting node {ent.get('name', 'N/A')}: {e}")

        # 2. 関係性の作成とプロパティ設定
        for rel in relations:
            try:
                rel_properties = rel.get('properties', {}) 
                logging.info(f"  Processing Relation: Start='{rel['start']}', End='{rel['end']}', Type='{rel['type']}', Props: {list(rel_properties.keys())}")

                session.run(f"""
                    MATCH (a {{name: $start_node_name}}), (b {{name: $end_node_name}})
                    MERGE (a)-[r:{rel['type']}]->(b)
                    SET r += $properties
                """, start_node_name=rel['start'], end_node_name=rel['end'], properties=rel_properties)
                logging.info(f"  MERGED Relation: ('{rel['start']}')-[:{rel['type']}]->('{rel['end']}')")
            except Exception as e:
                logging.error(f"  Error creating/setting relationship {rel.get('start', 'N/A')}-{rel.get('type', 'N/A')}-{rel.get('end', 'N/A')}: {e}")

        logging.info(f"Batch processing completed.")


def main():
    logging.info("--- 知識グラフの構築を開始します ---")

    all_documents = load_documents(KNOWLEDGE_BASE_DIR)
    if not all_documents:
        logging.error(f"エラー: {KNOWLEDGE_BASE_DIR} から対象ドキュメントを読み込めませんでした。知識グラフを構築できません。")
        return

    # 既存のグラフをクリア
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        logging.info("既存のグラフデータをクリアしました。")

    for doc in all_documents:
        source_path = doc.metadata.get("source", "unknown_source")
        logging.info(f"処理中ドキュメント: {source_path}")
        entities, relations = extract_entities_and_relations(doc.page_content, source_path)

        if entities or relations: 
            create_graph_nodes_and_relations(entities, relations)
        else:
            logging.info(f"  ドキュメント {source_path} からエンティティや関係性が見つかりませんでした。")

    logging.info("--- 知識グラフ構築完了！ ---")
    driver.close()

if __name__ == "__main__":
    main()