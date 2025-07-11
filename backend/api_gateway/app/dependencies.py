# backend/api_gateway/app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

# 関連するモジュールやサービスをインポート
from shared.db.session import SessionLocal
from shared.services.auth_service import AuthService
from shared.services.user_service import UserService
from shared.db.models import User
from shared.schemas import TokenData

# --- 依存関係を提供する関数の定義 ---

def get_db_session():
    """
    APIリクエストごとにデータベースセッションを提供する依存関係。
    リクエスト処理が完了したらセッションを閉じる。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_auth_service() -> AuthService:
    """AuthServiceのインスタンスを提供する依存関係。"""
    return AuthService()

def get_user_service(auth_service: AuthService = Depends(get_auth_service)) -> UserService:
    """UserServiceのインスタンスを提供する依存関係。AuthServiceに依存する。"""
    return UserService(auth_service=auth_service)


# --- 認証関連の依存関係 ---

# OAuth2のパスワードフローを定義。tokenUrlはログインエンドポイントを指定。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    リクエストヘッダーのJWTトークンを検証し、
    対応するユーザー情報をDBから取得する依存関係。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # トークンをデコードしてユーザー名を取得
    username = auth_service.decode_token(token)
    if username is None:
        raise credentials_exception
    
    # TokenDataスキーマで型を検証（必須ではないが堅牢性が増す）
    token_data = TokenData(username=username)

    # ユーザー名でDBからユーザー情報を取得
    user = user_service.get_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    （オプション）ユーザーがアクティブかどうかをチェックするための依存関係。
    Userモデルに is_active カラムを追加した場合などに利用。
    今回は単純に get_current_user を返すだけとする。
    """
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

