#!/bin/bash

# 色の設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Open WebUIの再ビルドと再起動を開始します${NC}"

# Dockerコンテナを停止して削除
echo -e "${YELLOW}既存のコンテナを停止して削除します...${NC}"
docker compose down
echo -e "${GREEN}コンテナの停止と削除が完了しました${NC}"

# Dockerイメージを再ビルド
echo -e "${YELLOW}Dockerイメージを再ビルドします...${NC}"
docker compose build --no-cache
echo -e "${GREEN}Dockerイメージの再ビルドが完了しました${NC}"

# Dockerコンテナを起動
echo -e "${YELLOW}新しいコンテナを起動します...${NC}"
docker compose up -d
echo -e "${GREEN}コンテナの起動が完了しました${NC}"

# ログの表示
echo -e "${YELLOW}コンテナのログを表示します...${NC}"
echo -e "${YELLOW}Ctrl+Cで終了できます${NC}"
docker compose logs -f