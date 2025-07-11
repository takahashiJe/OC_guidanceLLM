# backend/api_gateway/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Pythonがモジュールを探し始める場所を/app/backendに設定
ENV PYTHONPATH="/app/backend"

COPY ./backend/api_gateway/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# backendディレクトリ全体をコンテナにコピー
COPY ./backend/ /app/backend/

EXPOSE 8000

# ★★★ 修正点 ★★★
# uvicornの起動パスから`backend.`を削除
CMD ["uvicorn", "api_gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]