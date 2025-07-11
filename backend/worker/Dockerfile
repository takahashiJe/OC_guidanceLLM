# ベースイメージとして軽量なPython 3.11-slimを選択
FROM python:3.11-slim

# OSのパッケージを更新し、netcat（DB待機用）をインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# Pythonが/appディレクトリ内のモジュールを認識できるように環境変数を設定
ENV PYTHONPATH "${PYTHONPATH}:/app"

# 依存関係ファイルを先にコピーし、ビルドキャッシュを効率化
COPY ./backend/worker/requirements.txt /app/requirements.txt

# pipをアップグレードし、依存関係をインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# アプリケーションのコードをコピー
COPY ./backend/worker/ /app/worker/
COPY ./backend/shared/ /app/shared/

# entrypointスクリプトをコピー
COPY ./backend/worker/entrypoint.sh /app/entrypoint.sh

# entrypointスクリプトに実行権限を付与
RUN chmod +x /app/entrypoint.sh

# コンテナ起動時にentrypointスクリプトを実行
ENTRYPOINT ["/app/entrypoint.sh"]