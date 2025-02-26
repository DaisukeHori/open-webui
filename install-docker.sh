#!/bin/bash

# 色の設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}macOS用Dockerインストールガイド${NC}"
echo -e "${YELLOW}=============================${NC}"
echo ""
echo -e "1. ${GREEN}Docker Desktopをダウンロードしてインストールします${NC}"
echo "   ブラウザで以下のURLにアクセスしてください："
echo "   https://www.docker.com/products/docker-desktop/"
echo ""
echo -e "2. ${GREEN}ダウンロードしたDockerDesktop.dmgを開き、指示に従ってインストールします${NC}"
echo "   - Docker.appをApplicationsフォルダにドラッグ＆ドロップ"
echo "   - Launchpadから Docker を起動"
echo "   - 初回起動時に管理者パスワードの入力が必要な場合があります"
echo ""
echo -e "3. ${GREEN}インストール完了後、ターミナルでDockerが利用可能か確認します${NC}"
echo "   以下のコマンドを実行してください："
echo "   docker --version"
echo ""
echo -e "${YELLOW}インストール完了後、再度 ./rebuild.sh を実行してください${NC}"