# backend/api_gateway/app/chat_router.py

import uuid
from fastapi import APIRouter, Depends, HTTPException, status

# 依存関係、モデル、スキーマ、Celeryアプリケーションをインポート
from .dependencies import get_current_active_user
from worker.app.db.models import User
from shared.schemas import ChatInput, ChatResponse
from shared.celery_app import celery_app # Celeryインスタンス

# ルーターのインスタンスを作成
router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    # このルーターのすべてのエンドポイントは、認証を必須とする
    dependencies=[Depends(get_current_active_user)],
)

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_202_ACCEPTED)
def post_chat_message(
    chat_input: ChatInput,
    current_user: User = Depends(get_current_active_user),
):
    """
    認証済みユーザーからのチャットメッセージを受け付け、
    バックエンドの対話処理タスクを非同期で実行する。

    Args:
        chat_input: ユーザーからのメッセージとセッションID。
        current_user: 認証トークンから特定された現在のユーザー情報。

    Returns:
        非同期処理のタスクIDと現在のセッションIDを含むレスポンス。
    """
    if not chat_input.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="メッセージが空です。",
        )

    # セッションIDがクライアントから提供されない場合は、新しいIDを生成
    session_id = chat_input.session_id or str(uuid.uuid4())

    try:
        # Celeryタスクを呼び出す
        # 'worker.app.tasks.run_chat_graph' はCelery Worker側で定義するタスク名
        task = celery_app.send_task(
            'worker.app.tasks.run_chat_graph',
            args=[
                current_user.id,
                session_id,
                chat_input.message
            ]
        )
        
        # クライアントにタスクIDを返す
        return ChatResponse(task_id=task.id, session_id=session_id)

    except Exception as e:
        # Celeryブローカー（Redisなど）に接続できない場合のエラーハンドリング
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"非同期サービスの呼び出しに失敗しました: {e}",
        )

