# backend/shared/celery_app.py

import os
from celery import Celery

# 環境変数から接続情報を取得
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
redis_host = os.getenv('REDIS_HOST', 'localhost')

# Celeryの接続情報
broker_url = f'amqp://guest:guest@{rabbitmq_host}:5672//'
result_backend_url = f'redis://{redis_host}:6379/0'

# Celeryアプリケーションのインスタンスを作成
celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=result_backend_url,
    include=["worker.app.tasks"] # 実行するタスクが定義されているモジュールを指定
)

# Celeryの設定（オプション）
celery_app.conf.update(
    task_track_started=True,
)
