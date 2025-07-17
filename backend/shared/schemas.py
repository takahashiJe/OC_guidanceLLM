# backend/shared/schemas.py

from pydantic import BaseModel
from typing import Optional, Literal, List

# =======================================
# トークン関連のスキーマ
# =======================================

class Token(BaseModel):
    """
    /loginエンドポイントのレスポンスとして返すトークン情報。
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    JWTトークンのペイロード（中身）のデータ形式。
    """
    username: Optional[str] = None


# =======================================
# ユーザー関連のスキーマ
# =======================================

class UserBase(BaseModel):
    """
    ユーザーモデルの基本的なフィールドを定義するベースクラス。
    """
    username: str


class UserCreate(UserBase):
    """
    ユーザー新規作成時に受け取るデータ形式。
    パスワードを含む。
    """
    password: str


class UserPublic(UserBase):
    """
    APIレスポンスとしてクライアントに返すユーザー情報。
    パスワードなどの機密情報を含まない。
    """
    id: int

    class Config:
        # SQLAlchemyモデルなどのORMインスタンスからでもPydanticモデルに変換できるようにする
        orm_mode = True


# =======================================
# チャット関連のスキーマ
# =======================================

class ChatInput(BaseModel):
    """
    /chatエンドポイントでユーザーからの入力を受け取るためのデータ形式。
    """
    message: str
    session_id: Optional[str] = None # クライアント側でセッションを継続する場合


class ChatResponse(BaseModel):
    """
    /chatエンドポイントが即座に返すレスポンスのデータ形式。
    非同期処理のタスクIDを含む。
    """
    task_id: str
    session_id: str
    message: str = "対話処理を受け付けました。結果をポーリングしてください。"

class TaskResultResponse(BaseModel):
    """
    タスクの結果を取得するエンドポイントのレスポンス。
    """
    task_id: str
    status: Literal["PENDING", "SUCCESS", "FAILURE"]
    ai_message: Optional[str] = None
    detail: Optional[str] = None # 失敗時の詳細情報

class HistoryTurn(BaseModel):
    """
    会話履歴の1ターン分を表すスキーマ
    """
    human_message: str
    ai_message: str

    class Config:
        orm_mode = True

class LatestSessionResponse(BaseModel):
    """
    最新のセッションIDを返すためのスキーマ
    """
    session_id: Optional[str] = None