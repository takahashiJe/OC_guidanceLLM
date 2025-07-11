# ベースイメージとして軽量なPython 3.11-slimを選択
FROM python:3.11-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルを先にコピー
# ビルドコンテキスト（docker-compose.ymlがある場所）からの相対パスで指定
COPY ./backend/api_gateway/requirements.txt /app/requirements.txt

# pipをアップグレードし、依存関係をインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# アプリケーションのコードをコピー
# api_gatewayとsharedディレクトリをコンテナの/app/にコピー
COPY ./backend/api_gateway/ /app/api_gateway/
COPY ./backend/shared/ /app/shared/

# FastAPIアプリケーションがリッスンするポートを公開
EXPOSE 8000

# コンテナ起動時に実行するコマンド
# uvicornを使い、api_gateway/app/main.pyの中のappインスタンスを起動します
# --host 0.0.0.0 を指定して、コンテナ外部からのアクセスを許可します
CMD ["uvicorn", "api_gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]