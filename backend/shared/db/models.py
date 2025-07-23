# backend/worker/app/db/models.py

from sqlalchemy import Column, Integer, String, DateTime, func, Index, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

# SQLAlchemyのモデルを定義するための基本クラス
Base = declarative_base()

class User(Base):
    """
    ユーザー情報を格納するテーブル。
    ユーザー名とハッシュ化されたパスワードを持つ。
    """
    __tablename__ = 'users'

    # 1. システム内部で使う、不変の整数ID (主キー)
    id = Column(Integer, primary_key=True, autoincrement=True, comment="システム内部で利用する一意のユーザーID")
    
    # 2. ユーザーがログインに使う、固有のユーザー名
    username = Column(String(255), nullable=False, unique=True, index=True, comment="ログインに使用する固有のユーザー名")
    
    # 3. ハッシュ化されたパスワード
    hashed_password = Column(String(255), nullable=False, comment="ハッシュ化されたパスワード")
    
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="ユーザー作成日時")

    # UserとConversationHistoryの1対多の関係を定義
    histories = relationship("ConversationHistory", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class ConversationHistory(Base):
    """
    会話履歴を格納するためのテーブル。
    """
    __tablename__ = 'conversation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 外部キーとしてusersテーブルの「整数id」と関連付ける
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment="会話の所有者を示すユーザーID (users.id)")
    
    session_id = Column(String(255), nullable=False, comment="チャットセッションごとのID")
    turn = Column(Integer, nullable=False, comment="セッション内での会話のターン数")
    human_message = Column(Text, nullable=False)
    ai_message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # ConversationHistoryモデルからUserモデルにアクセスするためのリレーションシップ
    user = relationship("User", back_populates="histories")
    
    # 検索パフォーマンス向上のためのインデックス
    __table_args__ = (
        Index('ix_user_id_session_id', 'user_id', 'session_id'),
    )

    def __repr__(self):
        return f"<ConversationHistory(user_id={self.user_id}, session_id='{self.session_id}')>"

