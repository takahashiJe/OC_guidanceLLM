# script/load_knowledge.py

import os
import glob
from typing import List

from langchain.docstore.document import Document
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- 設定項目 ---

# 知識源となるMarkdownファイルが格納されているディレクトリ
KNOWLEDGE_BASE_DIR = "backend/worker/data/knowledge"
# ベクトル化されたデータを保存するChromaDBのディレクトリ
CHROMA_KNOWLEDGE_PATH = "backend/worker/data/vectorstore_knowledge"
# tasks.pyで使用しているものと同じEmbeddingモデルを指定
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"


def load_documents(directory: str) -> List[Document]:
    """指定されたディレクトリ内のすべてのMarkdownファイルを再帰的に読み込む"""
    md_files = glob.glob(os.path.join(directory, "**", "*.md"), recursive=True)
    documents = []
    for file_path in md_files:
        print(f"読み込み中: {file_path}")
        loader = UnstructuredMarkdownLoader(file_path)
        documents.extend(loader.load())
    return documents

def split_documents(documents: List[Document]) -> List[Document]:
    """Markdownの構造を考慮してドキュメントを分割（チャンキング）する"""
    md_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    return md_splitter.split_documents(documents)

def main():
    """
    メイン処理：
    1. Markdownファイルを読み込む
    2. ドキュメントを分割する
    3. 分割したドキュメントをベクトル化してChromaDBに保存する
    """
    print("--- 知識ベースの構築を開始します ---")

    # 1. ドキュメントの読み込みと分割
    print("\nステップ1: Markdownドキュメントの読み込みと分割...")
    all_documents = load_documents(KNOWLEDGE_BASE_DIR)
    if not all_documents:
        print("エラー: knowledgeディレクトリにMarkdownファイルが見つかりません。")
        return
    
    chunked_documents = split_documents(all_documents)
    print(f"ドキュメントの読み込み完了。合計 {len(chunked_documents)}個のチャンクに分割されました。")

    # 2. Embeddingモデルの初期化
    print("\nステップ2: Embeddingモデルの読み込み...")
    print(f"モデル名: {EMBEDDING_MODEL_NAME}")
    # この処理はモデルのダウンロードに時間がかかる場合があります
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    print("Embeddingモデルの読み込み完了。")

    # 3. ChromaDBへの保存
    print("\nステップ3: ドキュメントをベクトル化し、ChromaDBに保存...")
    print(f"保存先: {CHROMA_KNOWLEDGE_PATH}")
    
    # ChromaDBのインスタンスを作成し、ドキュメントを保存
    # 既存のDBがある場合は上書きされます
    vectorstore = Chroma.from_documents(
        documents=chunked_documents,
        embedding=embedding_model,
        persist_directory=CHROMA_KNOWLEDGE_PATH,
    )
    
    # データを永続化
    vectorstore.persist()
    
    print("\n--- 知識ベースの構築が正常に完了しました！ ---")


if __name__ == "__main__":
    # このスクリプトが直接実行された場合にmain関数を呼び出す
    main()

