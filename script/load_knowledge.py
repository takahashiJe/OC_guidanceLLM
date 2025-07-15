# backend/worker/script/load_knowledge.py

import os
import sys
import logging

# --- ロギング設定 ---
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# --- パス設定 ---
try:
    _current_file_path = os.path.abspath(__file__)
    _script_dir = os.path.dirname(_current_file_path)
    _project_root = os.path.dirname(_script_dir)
    sys.path.append(_project_root)
except NameError:
    # 対話モード用のフォールバック
    sys.path.append(os.getcwd())


from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader, JSONLoader
# ★★★ メタデータをフィルタリングする関数をインポート ★★★
from langchain_community.vectorstores.utils import filter_complex_metadata

# --- 定数設定 ---
KNOWLEDGE_BASE_DIR = "backend/worker/data/knowledge"
VECTORSTORE_PATH = "backend/worker/data/vectorstore_knowledge"
EMBEDDINGS = OllamaEmbeddings(model="mxbai-embed-large", base_url="http://ollama:11434")

def split_documents(documents):
    # チャンクサイズとオーバーラップを調整 (ハルシネーション対策)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    return text_splitter.split_documents(documents)

def load_documents(directory: str):
    all_docs = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.endswith(".md"):
                    loader = UnstructuredMarkdownLoader(file_path, mode="elements")
                    all_docs.extend(loader.load())
                elif file.endswith(".json"):
                    loader = JSONLoader(file_path=file_path, jq_schema='.', text_content=False)
                    all_docs.extend(loader.load())
            except Exception as e:
                logging.error(f"ファイルの読み込み中にエラー: {file_path}, 詳細: {e}")
    return all_docs

def split_documents(documents):
    # ★★★ chunk_sizeとchunk_overlapの値を変更 ★★★
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50) # 1000, 100 から変更
    return text_splitter.split_documents(documents)

def main():
    logging.info("--- 知識ベースの構築を開始します ---")

    logging.info("\nステップ1: ドキュメントの読み込み...")
    all_documents = load_documents(KNOWLEDGE_BASE_DIR)
    if not all_documents:
        logging.error(f"エラー: {KNOWLEDGE_BASE_DIR} からドキュメントを読み込めませんでした。")
        return
    
    # ★★★ ステップ1.5: 複雑なメタデータをフィルタリング ★★★
    logging.info("\nステップ1.5: 複雑なメタデータをフィルタリング...")
    filtered_documents = filter_complex_metadata(all_documents)
    logging.info("メタデータのフィルタリングが完了しました。")


    logging.info("\nステップ2: ドキュメントの分割...")
    split_docs = split_documents(filtered_documents) # フィルター済みのドキュメントを分割
    logging.info(f"ドキュメントの分割完了。合計 {len(split_docs)}個のチャンク。")
    
    logging.info("\nステップ3: Embeddingモデルの確認...")
    logging.info(f"モデル名: nomic-embed-text (Ollama経由)")

    logging.info("\nステップ4: ドキュメントをベクトル化し、ChromaDBに保存...")
    logging.info(f"保存先: {VECTORSTORE_PATH}")
    
    try:
        vectorstore = Chroma.from_documents(
            documents=split_docs, # 分割済みのチャンクを渡す
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
        logging.error("!!! ベクトルストアの作成中に致命的なエラーが発生しました。")
        logging.error(f"エラー詳細: {e}", exc_info=True)


if __name__ == "__main__":
    main()