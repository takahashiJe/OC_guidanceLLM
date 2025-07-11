# backend/worker/app/services/user_service.py

from typing import Optional
from sqlalchemy.orm import Session

from shared.db.models import User
from shared.schemas import UserCreate # Pydanticモデルをsharedからインポート
from .auth_service import AuthService


class UserService:
    """
    ユーザー情報のCRUD（作成、読み取り、更新、削除）操作を担当するサービスクラス。
    """

    def __init__(self, auth_service: AuthService):
        """
        UserServiceを初期化します。
        認証サービスに依存し、パスワードのハッシュ化などに利用します。

        Args:
            auth_service: AuthServiceのインスタンス。
        """
        self.auth_service = auth_service

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        ユーザー名でユーザー情報をデータベースから取得します。

        Args:
            db: SQLAlchemyのセッションオブジェクト。
            username: 検索するユーザー名。

        Returns:
            見つかったUserモデルのインスタンス。見つからなければNone。
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        ユーザーID（整数）でユーザー情報をデータベースから取得します。

        Args:
            db: SQLAlchemyのセッションオブジェクト。
            user_id: 検索するユーザーのID。

        Returns:
            見つかったUserモデルのインスタンス。見つからなければNone。
        """
        return db.query(User).filter(User.id == user_id).first()

    def create(self, db: Session, user_create: UserCreate) -> User:
        """
        新規ユーザーを作成し、データベースに保存します。
        パスワードはハッシュ化してから保存します。

        Args:
            db: SQLAlchemyのセッションオブジェクト。
            user_create: 作成するユーザーの情報（ユーザー名と平文パスワード）。

        Returns:
            作成されたUserモデルのインスタンス。
        """
        # 平文のパスワードをハッシュ化
        hashed_password = self.auth_service.get_password_hash(user_create.password)
        
        # 新しいUserモデルインスタンスを作成
        db_user = User(
            username=user_create.username,
            hashed_password=hashed_password
        )
        
        # データベースセッションに追加し、コミットして永続化
        db.add(db_user)
        db.commit()
        
        # DBによって自動採番されたIDなどを含むインスタンスをリフレッシュ
        db.refresh(db_user)
        
        return db_user

