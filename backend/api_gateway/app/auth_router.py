# backend/api_gateway/app/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# 依存関係とサービス、スキーマをインポート
# (これらのファイルは別途作成・更新が必要です)
from .dependencies import get_db_session, get_user_service, get_auth_service
from shared.services.user_service import UserService
from shared.services.auth_service import AuthService
from shared.schemas import UserCreate, UserPublic, Token

# ルーターのインスタンスを作成
router = APIRouter(
    prefix="/auth",  # このルーターのエンドポイントはすべて "/auth" で始まる
    tags=["Authentication"], # FastAPIのドキュメントでグループ化するためのタグ
)

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
):
    """
    新規ユーザーを登録するためのエンドポイント。
    成功すると、作成されたユーザー情報（パスワードなし）を返す。
    """
    # ユーザー名が既に存在するかチェック
    db_user = user_service.get_by_username(db, username=user_create.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に使用されています。",
        )
    
    # ユーザーを作成
    created_user = user_service.create(db, user_create=user_create)
    return created_user


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    ユーザーを認証し、JWTアクセストークンを発行するためのエンドポイント。
    """
    # ユーザー名でユーザーを検索
    user = user_service.get_by_username(db, username=form_data.username)
    
    # ユーザーが存在しない、またはパスワードが間違っている場合
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません。",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # アクセストークンを生成
    # トークンのペイロード（中身）には、ユーザーを識別するための情報（ここではユーザー名）を入れる
    access_token = auth_service.create_access_token(
        data={"sub": user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# (参考) 保護されたエンドポイントで現在のユーザーを取得するための依存関係
# from .dependencies import get_current_active_user
# from worker.app.db.models import User
# @router.get("/users/me", response_model=UserPublic)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#    """
#    認証済みのユーザー自身の情報を取得するエンドポイント。
#    """
#    return current_user

