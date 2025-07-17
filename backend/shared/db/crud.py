from sqlalchemy.orm import Session
from . import models
from typing import List
from sqlalchemy import func
from typing import List, Optional

def get_history_by_session_id(db: Session, session_id: str, user_id: int):
    """
    ユーザーIDとセッションIDに基づいて、最新5件の会話履歴を取得する。
    """
    return (
        db.query(models.ConversationHistory)
        .filter(
            models.ConversationHistory.user_id == user_id,
            models.ConversationHistory.session_id == session_id,
        )
        .order_by(models.ConversationHistory.turn.desc())
        .limit(5)
        .all()
    )

def create_history_record(
    db: Session,
    user_id: int,
    session_id: str,
    turn: int,
    human_message: str,
    ai_message: str,
):
    """
    新しい会話のターンをデータベースに保存する。
    """
    db_history = models.ConversationHistory(
        user_id=user_id,
        session_id=session_id,
        turn=turn,
        human_message=human_message,
        ai_message=ai_message,
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_history_by_session_id_all(db: Session, session_id: str, user_id: int) -> List[models.ConversationHistory]:
    """
    指定されたセッションの全ての会話履歴を、投稿順（昇順）に取得する。
    """
    return (
        db.query(models.ConversationHistory)
        .filter(
            models.ConversationHistory.user_id == user_id,
            models.ConversationHistory.session_id == session_id,
        )
        .order_by(models.ConversationHistory.turn.asc()) # asc()で古い順に並び替え
        .all()
    )

def get_latest_session_id(db: Session, user_id: int) -> Optional[str]:
    """
    指定されたユーザーIDの、最も新しい会話セッションのIDを取得する。
    """
    latest_session = (
        db.query(models.ConversationHistory.session_id)
        .filter(models.ConversationHistory.user_id == user_id)
        .group_by(models.ConversationHistory.session_id)
        .order_by(func.max(models.ConversationHistory.created_at).desc()) # 最終更新日時で降順ソート
        .first() # 最初の1件のみ取得
    )
    
    # 結果が存在すればsession_idを、存在しなければNoneを返す
    return latest_session.session_id if latest_session else None