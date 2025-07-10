# backend/api_gateway/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 作成したルーターをインポート
from . import auth_router
# from . import chat_router # chat_routerも後で同様にインポートする

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI(
    title="大学オープンキャンパス案内LLMシステム API",
    description="ユーザー認証と対話機能を提供するAPIです。",
    version="1.0.0",
)

# CORS (Cross-Origin Resource Sharing) ミドルウェアの設定
# これにより、異なるドメインで動作するフロントエンド（Vue.js）からのリクエストを許可する
origins = [
    "http://localhost",
    "http://localhost:8080", # Vue.js開発サーバーのデフォルトポート
    "http://localhost:5173", # Viteを利用したVue.js開発サーバーのデフォルトポート
    # 本番環境のフロントエンドのURLもここに追加する
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # すべてのHTTPメソッドを許可
    allow_headers=["*"], # すべてのHTTPヘッダーを許可
)


# アプリケーションにルーターを登録
app.include_router(auth_router.router)
# app.include_router(chat_router.router) # chat_routerも後で登録する

@app.get("/", tags=["Root"])
def read_root():
    """
    APIサーバーが正常に動作しているかを確認するためのルートエンドポイント。
    """
    return {"message": "Welcome to the Open Campus Guidance LLM API!"}

