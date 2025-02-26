#!/bin/bash

# 色の設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Homebrewを使用したDocker/Docker Composeのインストール${NC}"
echo -e "${YELLOW}==========================================${NC}"
echo ""

# Homebrewがインストールされているか確認
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Homebrewがインストールされていません。まずHomebrewをインストールします...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo -e "${GREEN}Homebrewのインストールが完了しました${NC}"
else
    echo -e "${GREEN}Homebrewは既にインストールされています${NC}"
fi

# Dockerのインストール
echo -e "${YELLOW}Dockerをインストールします...${NC}"
brew install --cask docker
echo -e "${GREEN}Dockerのインストールが完了しました${NC}"

# Docker Composeのインストール（Docker for Macに含まれているが念のため）
echo -e "${YELLOW}Docker Composeをインストールします...${NC}"
brew install docker-compose
echo -e "${GREEN}Docker Composeのインストールが完了しました${NC}"

# Dockerアプリケーションを起動
echo -e "${YELLOW}Dockerアプリケーションを起動します...${NC}"
open -a Docker
echo -e "${GREEN}Dockerアプリケーションを起動しました${NC}"
echo "Dockerが完全に起動するまで少し時間がかかります。"
echo "Dockerのステータスアイコンが安定するまでお待ちください。"

echo ""
echo -e "${YELLOW}インストールが完了しました。Dockerが完全に起動したら、以下のコマンドでバージョンを確認できます：${NC}"
echo "docker --version"
echo "docker-compose --version"
echo ""
echo -e "${YELLOW}その後、./rebuild.sh を実行してOpen WebUIを再ビルドしてください。${NC}"