# verify_rag.py

import sys
# backend/workerをパスに追加して、OllamaEmbeddingsなどをインポートできるようにする
sys.path.append('./backend/worker')

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

print("--- RAG診断スクリプトを開始します ---")

# --- 設定 ---
# tasks.pyと同じ設定を使用
EMBEDDINGS = OllamaEmbeddings(model="mxbai-embed-large", base_url="http://ollama:11434")
CHROMA_KNOWLEDGE_PATH = "/app/worker/data/vectorstore_knowledge"
TEST_QUERY = "サイバーフィジカルシステム研究室（山口研）のオープンキャンパス出展内容を教えてください"

try:
    # 1. 既存のベクトルストアを読み込む
    print(f"ベクトルストアを読み込みます: {CHROMA_KNOWLEDGE_PATH}")
    vectorstore = Chroma(
        persist_directory=CHROMA_KNOWLEDGE_PATH, 
        embedding_function=EMBEDDINGS
    )
    print("ベクトルストアの読み込みに成功しました。")
    print(f"データベース内のドキュメント総数: {vectorstore._collection.count()}")

    # 2. 類似度検索を実行
    print(f"\n以下のクエリで検索を実行します:\n'{TEST_QUERY}'")
    retrieved_docs = vectorstore.similarity_search(TEST_QUERY, k=10)

    # 3. 結果を表示
    if not retrieved_docs:
        print("\n--- 診断結果: 失敗 ---")
        print("エラー: 関連するドキュメントが見つかりませんでした。")
        print("考えられる原因:")
        print("  - ベクトルストアが空か、正しく構築されていません。")
        print("  - `load_knowledge.py`の実行が失敗している可能性があります。")
    else:
        print("\n--- 診断結果: 成功 ---")
        print(f"{len(retrieved_docs)}件の関連ドキュメントが見つかりました：")
        for i, doc in enumerate(retrieved_docs):
            print(f"\n--- [ドキュメント {i+1}] ---")
            print(f"ソース: {doc.metadata.get('source', 'N/A')}")
            print(f"内容抜粋: {doc.page_content[:150]}...")

except Exception as e:
    print("\n--- 診断結果: エラー ---")
    print(f"スクリプトの実行中にエラーが発生しました: {e}")
    print("Ollamaコンテナが起動しているか、パスが正しいかを確認してください。")
