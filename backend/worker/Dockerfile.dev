# backend/worker/Dockerfile

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pythonがモジュールを探し始める場所を/app/backendに設定
ENV PYTHONPATH="/app/backend"

COPY ./backend/worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    python -m spacy download ja_core_news_sm --no-deps

# backendディレクトリ全体をコンテナにコピー
COPY ./backend/ /app/backend/

COPY ./backend/worker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]