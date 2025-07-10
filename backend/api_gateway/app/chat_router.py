from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from app.dependencies import get_db_session, get_current_user
from app.schemas.chat import ChatInput, ChatResponse
from app.schemas.user import User
from app.celery_app import celery_app
# kombuライブラリから、より具体的な接続エラーをインポートします
from kombu.exceptions import OperationalError

router = APIRouter()


@router.post("", response_model=ChatResponse)
def post_chat_message(
    chat_input: ChatInput,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    ユーザーからのチャットメッセージを受け取り、非同期タスクとして処理を開始するエンドポイント。
    """
    session_id = chat_input.session_id or str(uuid4())

    try:
        # Celeryタスクを呼び出す
        task = celery_app.send_task(
            'worker.app.tasks.run_chat_graph',
            args=[
                current_user.id,
                session_id,
                chat_input.message
            ]
        )
        
        return ChatResponse(task_id=task.id, session_id=session_id)

    # ★修正点 1: OperationalErrorを明示的に捕捉
    # これにより、Redis等のメッセージブローカーに接続できない問題を検知します。
    except OperationalError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"メッセージブローカーへの接続に失敗しました。サービスが一時的に利用できない可能性があります。",
        )
    
    # ★修正点 2: 予期せぬエラーのための汎用的な例外ハンドリング
    # OperationalError以外の問題が発生した場合にも、サーバーエラーとして処理します。
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"非同期サービスの呼び出し中に予期せぬエラーが発生しました: {e}",
        )