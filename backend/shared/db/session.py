# backend/worker/app/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# データベース接続URLを環境変数から取得
# .envファイルで設定することを想定: DATABASE_URL="mysql+pymysql://user:password@host/dbname"
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@mysql/app_db")

# データベースエンジンを作成
# connect_argsはSQLite利用時以外は通常不要ですが、文字化け対策などで利用することがあります
engine = create_engine(
    DATABASE_URL,
    # pool_pre_ping=True # 本番環境では接続の有効性を確認するために推奨
)

# データベースセッションを作成するためのクラスを定義
# autocommit=False, autoflush=Falseが標準的な設定です
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    （オプション）開発初期にテーブルを一度に作成するための関数。
    本番環境ではAlembicなどのマイグレーションツールを使うべきです。
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)

