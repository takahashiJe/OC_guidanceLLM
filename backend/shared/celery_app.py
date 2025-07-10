# backend/shared/celery_app.py

from celery import Celery
from backend.worker.app.core.config import settings

# Celeryアプリケーションのインスタンスを作成
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["backend.worker.app.tasks"] # 実行するタスクが定義されているモジュールを指定
)

# Celeryの設定（オプション）
celery_app.conf.update(
    task_track_started=True,
)
