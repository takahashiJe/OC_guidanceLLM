#!/bin/sh

# Pythonがモジュールを見つけられるようにPYTHONPATHを設定
export PYTHONPATH="/app"

# --- データベースの接続待機 ---
# docker-compose.ymlで定義するDBのホスト名（例: db）を環境変数から取得
echo "Waiting for Database to be ready..."

# データベースの準備ができるまで待機するループ
# docker-compose.ymlのDBホスト名を`db`と想定
until nc -z -v -w30 db 3306
do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready!"

# ★★★ データベース初期化スクリプトは削除 ★★★

# --- Celery Workerの起動 ---
echo "Starting Celery worker for GPU..."
# -P solo を追加して、単一プロセスでタスクを実行するように指定
exec celery -A shared.celery_app.celery_app worker --loglevel=info -P solo