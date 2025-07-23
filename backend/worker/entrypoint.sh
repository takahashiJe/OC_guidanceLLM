#!/bin/sh

# PYTHONPATHはDockerfileのENVで設定するため、ここでのexportは不要

echo "Waiting for Database at ${DB_HOST:-db}:${DB_PORT:-3306}..."
until nc -z -v -w30 ${DB_HOST:-db} ${DB_PORT:-3306}
do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is ready!"

echo "Starting Celery worker for GPU..."
# ★★★ 修正点 ★★★
# Celeryアプリケーションのパスから`backend.`を削除
# exec celery -A shared.celery_app.celery_app worker --loglevel=info -P solo
exec celery -A shared.celery_app.celery_app worker --loglevel=info --pool=threads --concurrency=1

