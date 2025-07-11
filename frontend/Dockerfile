# ベースイメージとしてNode.jsを選択
FROM node:20

# 作業ディレクトリを設定
WORKDIR /app

# package.jsonとlockファイルを先にコピーして、依存関係をインストール
# これにより、依存関係に変更がない限り、再インストールがスキップされビルドが高速化する
COPY package*.json ./
RUN npm install

# ソースコードをコピー (開発時はvolumesで上書きされる)
COPY . .

# 開発サーバーがリッスンするポートを公開
EXPOSE 5173

# 開発サーバーを起動
CMD ["npm", "run", "dev"]