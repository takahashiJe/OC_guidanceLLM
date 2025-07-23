# backend/api_gateway/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 作成したルーターをインポート
from . import auth_router
from . import chat_router

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI(
    title="大学オープンキャンパス案内LLMシステム API",
    description="ユーザー認証と対話機能を提供するAPIです。",
    version="1.0.0",
)

# CORS (Cross-Origin Resource Sharing) ミドルウェアの設定
origins = [
    "http://localhost",
    "http://localhost:80", # フロントエンドがポート80で動作する場合
    "http://localhost:8080",
    "http://localhost:5173",
    "https://ibera.cps.akita-pu.ac.jp"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# アプリケーションにルーターを登録
app.include_router(auth_router.router)
app.include_router(chat_router.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    APIサーバーが正常に動作しているかを確認するためのルートエンドポイント。
    """
    return {"message": "Welcome to the Open Campus Guidance LLM API!"}