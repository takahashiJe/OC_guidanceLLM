# backend/worker/app/core/config.py

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    環境変数から設定値を読み込むための設定クラス。
    .envファイルが自動的に読み込まれます。
    """
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@mysql/app_db"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # JWT
    SECRET_KEY: str = "your-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Ollama
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3:8b-instruct-q5_K_M"
    
    # RAG
    EMBEDDING_MODEL_NAME: str = "intfloat/multilingual-e5-large"
    CHROMA_KNOWLEDGE_PATH: str = "/app/backend/worker/data/vectorstore_knowledge"
    CHROMA_MEMORY_PATH: str = "/app/backend/worker/data/vectorstore_memory"


    class Config:
        # .envファイルを読み込む設定
        env_file = ".env"
        env_file_encoding = 'utf-8'

# 設定クラスのインスタンスを作成
settings = Settings()
