from sqlalchemy.orm import Session
from . import models

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