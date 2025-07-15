# backend/worker/app/rag/retriever.py

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.embeddings import OllamaEmbeddings

from backend.worker.app.core.config import settings

def get_retriever() -> VectorStoreRetriever:
    """
    知識ベース用のChromaDBから情報を検索するためのRetrieverを初期化して返す。
    """
    # Embeddingモデルを初期化
    embedding_model = OllamaEmbeddings(model="mxbai-embed-large", base_url="http://ollama:11434")

    # 永続化されたChromaDBに接続
    vectorstore_knowledge = Chroma(
        persist_directory=settings.CHROMA_KNOWLEDGE_PATH,
        embedding_function=embedding_model,
    )

    # Retrieverを作成して返す
    return vectorstore_knowledge.as_retriever(search_kwargs={"k": 3})

