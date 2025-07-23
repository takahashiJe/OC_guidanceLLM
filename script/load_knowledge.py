# backend/worker/script/load_knowledge.py

import os
import sys
import logging
import json
from typing import List, Dict, Any

# --- パス設定 ---
try:
    _current_file_path = os.path.abspath(__file__)
    _script_dir = os.path.dirname(_current_file_path)
    _project_root = os.path.dirname(os.path.dirname(_script_dir))
    if _project_root not in sys.path:
        sys.path.append(_project_root)
except NameError:
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- ロギング設定 ---
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# --- 定数設定 ---
KNOWLEDGE_BASE_DIR = "backend/worker/data/knowledge"
VECTORSTORE_PATH = "/app/worker/data/vectorstore_knowledge"
EMBEDDINGS = OllamaEmbeddings(model="mxbai-embed-large", base_url="http://ollama:11434")
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SHORT_DOC_THRESHOLD = 500


def parse_metadata_from_path(file_path: str) -> Dict[str, Any]:
    """
    ファイルのパスから階層的なメタデータを抽出する。
    """
    relative_path = os.path.relpath(file_path, KNOWLEDGE_BASE_DIR)
    parts = relative_path.split(os.sep)
    
    metadata = {"source": os.path.basename(file_path)}
    
    if len(parts) > 1:
        metadata["category_l1"] = parts[0][3:] if parts[0][:2].isdigit() and parts[0][2] == '_' else parts[0]
    if len(parts) > 2 and "学部" in parts[1]:
        metadata["faculty"] = parts[1]
    if len(parts) > 3 and "学科" in parts[2]:
        metadata["department"] = parts[2][3:] if parts[2][:2].isdigit() and parts[2][2] == '_' else parts[2]
    if len(parts) > 4 and "研究室" in parts[3]:
        metadata["lab"] = parts[4]
    if "出展詳細" in parts:
        metadata["document_type"] = "出展詳細"
        
    return metadata

# ★★★ ここから修正 ★★★
def convert_json_to_text(data: Any, metadata: Dict[str, Any]) -> str:
    """
    JSONデータを、メタデータに基づいて文脈を付与した自然言語テキストに変換する。
    timetable形式（リスト）の場合のみ処理する。
    """
    # データがリスト形式でなければ処理しない
    if not isinstance(data, list):
        logging.warning(f"JSONファイル '{metadata.get('source')}' はtimetable形式（リスト）ではないため、スキップします。")
        return ""

    texts = []
    context_info = []
    if "lab" in metadata:
        context_info.append(f"{metadata['lab']}の")
    elif "department" in metadata:
        context_info.append(f"{metadata['department']}の")
    context_prefix = "".join(context_info)

    for item in data:
        # リストの各要素が辞書でなければスキップ
        if not isinstance(item, dict):
            continue

        event_name = item.get("event_name", "名称未定のイベント")
        location = item.get("location", "場所未定")
        description = item.get("description")
        presenter = item.get("presenter")
        start_time = item.get("start_time")
        end_time = item.get("end_time")

        text = f"{context_prefix}イベント「{event_name}」は、{location}で開催されます。"
        if start_time and end_time:
            text += f"時間は{start_time}から{end_time}までです。"
        if description:
            text += f"イベント内容は「{description}」です。"
        if presenter:
            text += f"担当は{presenter}さんです。"
        texts.append(text)
            
    return "\n\n".join(texts)
# ★★★ ここまで修正 ★★★

def load_and_prepare_documents(directory: str) -> List[Document]:
    """
    ディレクトリを走査し、各ファイルをDocumentオブジェクトとして読み込む。
    """
    prepared_docs = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith('.'): continue
            file_path = os.path.join(root, file)
            metadata = parse_metadata_from_path(file_path)
            
            try:
                if file.endswith(".md"):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    prepared_docs.append(Document(page_content=content, metadata=metadata))
                
                elif file.endswith(".json"):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    content = convert_json_to_text(data, metadata)
                    if content:
                        prepared_docs.append(Document(page_content=content, metadata=metadata))
            except Exception as e:
                logging.error(f"ファイルの読み込み中にエラー: {file_path}, 詳細: {e}")
    return prepared_docs

def split_documents(documents: List[Document]) -> List[Document]:
    """
    ドキュメントの種類に応じて最適な方法で分割（チャンキング）する。
    """
    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    all_chunks = []
    for doc in documents:
        if len(doc.page_content) <= SHORT_DOC_THRESHOLD:
            all_chunks.append(doc)
            continue

        if doc.metadata.get("source", "").endswith(".md"):
            md_header_chunks = markdown_splitter.split_text(doc.page_content)
            
            for chunk in md_header_chunks:
                if len(chunk.page_content) > CHUNK_SIZE:
                    sub_chunks = text_splitter.create_documents([chunk.page_content])
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata.update(chunk.metadata)
                        sub_chunk.metadata.update(doc.metadata)
                    all_chunks.extend(sub_chunks)
                else:
                    chunk.metadata.update(doc.metadata)
                    all_chunks.append(chunk)
        else:
            chunks = text_splitter.split_documents([doc])
            all_chunks.extend(chunks)
            
    return all_chunks


def main():
    logging.info("--- 知識ベースの構築を開始します ---")

    logging.info("\nステップ1: ドキュメントの読み込みと前処理...")
    prepared_documents = load_and_prepare_documents(KNOWLEDGE_BASE_DIR)
    if not prepared_documents:
        logging.error(f"エラー: {KNOWLEDGE_BASE_DIR} からドキュメントを読み込めませんでした。")
        return
    logging.info(f"合計 {len(prepared_documents)} ファイルを処理対象として読み込みました。")

    logging.info("\nステップ2: ドキュメントの分割 (ハイブリッド・チャンキング)...")
    split_chunks = split_documents(prepared_documents)
    logging.info(f"ドキュメントの分割完了。合計 {len(split_chunks)} 個のチャンクを作成しました。")
    
    if split_chunks:
        logging.info("--- 生成されたチャンクの例 ---")
        for i, chunk in enumerate(split_chunks[:2] + split_chunks[-2:]):
            content_preview = chunk.page_content[:150].strip().replace('\n', ' ')
            logging.info(f"  [チャンク {i}] メタデータ: {chunk.metadata}")
            logging.info(f"  内容抜粋: {content_preview}...")
        logging.info("--------------------------")

    logging.info("\nステップ3: Embeddingモデルの確認...")
    logging.info(f"モデル名: {EMBEDDINGS.model} (Ollama経由)")

    logging.info("\nステップ4: ドキュメントをベクトル化し、ChromaDBに保存...")
    logging.info(f"保存先: {VECTORSTORE_PATH}")
    
    if not split_chunks:
        logging.warning("!!! 警告: 保存対象のチャンクがありません。処理を終了します。")
        return

    try:
        vectorstore = Chroma.from_documents(
            documents=split_chunks,
            embedding=EMBEDDINGS,
            persist_directory=VECTORSTORE_PATH
        )
        
        collection_count = vectorstore._collection.count()
        logging.info(f"ベクトルストアへの保存が完了。DB内のドキュメント総数: {collection_count}")
        
        if collection_count > 0:
             logging.info("\n--- 知識ベースの構築が正常に完了しました！ ---")
        else:
             logging.warning("!!! 警告: データベースへの保存処理は成功しましたが、ドキュメント数が0です。")

    except Exception as e:
        logging.error("!!! ベクトルストアの作成中に致命的なエラーが発生しました。", exc_info=True)


if __name__ == "__main__":
    main()