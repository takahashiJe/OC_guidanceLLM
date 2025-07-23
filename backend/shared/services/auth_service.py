# backend/worker/app/services/auth_service.py

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# パスワードハッシュ化のためのコンテキストを設定
# bcryptは強力で推奨されるハッシュアルゴリズムです
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWTトークンの設定を環境変数から読み込む
# これらは.envファイルで管理します
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class AuthService:
    """
    認証関連のロジックを担当するサービスクラス。
    パスワードの検証、ハッシュ化、JWTトークンの生成・検証を行う。
    """

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        平文のパスワードとハッシュ化されたパスワードが一致するかを検証します。

        Args:
            plain_password: ユーザーが入力した平文のパスワード。
            hashed_password: データベースに保存されているハッシュ化されたパスワード。

        Returns:
            パスワードが一致すればTrue、そうでなければFalse。
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        平文のパスワードをハッシュ化します。

        Args:
            password: ハッシュ化する平文のパスワード。

        Returns:
            ハッシュ化されたパスワード文字列。
        """
        return pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        JWTアクセストークンを生成します。

        Args:
            data: トークンに含めるデータ（ペイロード）。通常はユーザー名やID。
            expires_delta: トークンの有効期限。指定がなければデフォルト値を使用。

        Returns:
            エンコードされたJWTトークン文字列。
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[str]:
        """
        JWTトークンをデコードし、ペイロードからユーザー名を抽出します。
        FastAPIの依存性注入で直接使われることが多いです。

        Args:
            token: デコードするJWTトークン。

        Returns:
            トークンが有効であればユーザー名、無効であればNone。
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None

