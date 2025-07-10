from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID

class ChatInput(BaseModel):
    """
    POST /chat でユーザーからの入力を受け取るためのデータ形式。
    """
    message: str
    session_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    """
    POST /chat が即座に返すレスポンスのデータ形式。
    """
    task_id: str
    session_id: str
    message: str = "対話処理を受け付けました。結果をポーリングしてください。"

# ★★★★★ ここから追加 ★★★★★
class TaskResultResponse(BaseModel):
    """
    GET /chat/results/{task_id} が返すレスポンスのデータ形式。
    """
    task_id: str
    status: Literal["PENDING", "SUCCESS", "FAILURE"]
    ai_message: Optional[str] = None
    detail: Optional[str] = None # 失敗時の詳細情報