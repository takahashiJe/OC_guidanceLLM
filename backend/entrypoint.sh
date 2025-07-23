#!/bin/bash

# スクリプトのいずれかのコマンドが失敗した場合、直ちに終了する
set -e

echo "データベースの準備が完了するのを待っています..."

# 手順1で作成したPythonスクリプトを実行してDBを初期化
# このスクリプト内でDB接続のリトライが行われる
python /app/script/init_db.py

echo "データベースの準備完了。アプリケーションを起動します。"

# entrypoint.shに渡された引数をメインのコマンドとして実行
# (DockerfileのCMDで指定された "uvicorn..." がここで実行される)
exec "$@"
