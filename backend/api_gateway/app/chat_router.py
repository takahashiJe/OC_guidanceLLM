from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from celery.result import AsyncResult # Celeryの結果オブジェクトをインポート
from kombu.exceptions import OperationalError
from shared.schemas import ChatInput, ChatResponse, TaskResultResponse

from app.dependencies import get_db_session, get_current_user
from app.schemas.user import User
from app.celery_app import celery_app

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    dependencies=[Depends(get_current_user)]
)


@router.post("", response_model=ChatResponse, status_code=status.HTTP_202_ACCEPTED)
def post_chat_message(
    chat_input: ChatInput,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    ユーザーからのチャットメッセージを受け取り、非同期タスクとして処理を開始する。
    """
    session_id = str(chat_input.session_id) if chat_input.session_id else str(uuid4())

    try:
        task = celery_app.send_task(
            'worker.app.tasks.run_chat_graph',
            args=[current_user.id, session_id, chat_input.message]
        )
        return ChatResponse(task_id=task.id, session_id=session_id)
    except OperationalError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"メッセージブローカーへの接続に失敗しました。サービスが一時的に利用できない可能性があります。",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"非同期サービスの呼び出し中に予期せぬエラーが発生しました: {e}",
        )


# ★★★★★ ここから追加 ★★★★★
@router.get("/results/{task_id}", response_model=TaskResultResponse)
def get_task_result(task_id: str, current_user: User = Depends(get_current_user)):
    """
    タスクIDを指定して、非同期処理の結果を取得する。
    フロントエンドは、このエンドポイントをポーリングする。
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if not task_result.ready():
        # タスクがまだ完了していない場合
        return TaskResultResponse(task_id=task_id, status="PENDING")
    
    if task_result.successful():
        # タスクが成功した場合
        result = task_result.get()
        return TaskResultResponse(
            task_id=task_id,
            status="SUCCESS",
            ai_message=result
        )
    else:
        # タスクが失敗した場合
        error_info = str(task_result.info)
        return TaskResultResponse(
            task_id=task_id,
            status="FAILURE",
            detail=error_info
        )