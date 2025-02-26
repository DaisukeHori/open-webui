#!/bin/bash

# このスクリプトはOpen WebUIをフォークし、カスタマイズするための手順を自動化します

# 色の設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Open WebUIのフォークとカスタマイズセットアップを開始します${NC}"

# GitHubユーザー名の入力
read -p "GitHubユーザー名を入力してください: " GITHUB_USERNAME

# 現在のディレクトリ名を取得
CURRENT_DIR=$(basename "$PWD")

# リモートの確認
if git remote -v | grep -q "origin.*open-webui/open-webui"; then
  echo -e "${GREEN}Open WebUIリポジトリが正しくクローンされています${NC}"
else
  echo -e "${YELLOW}警告: このディレクトリはOpen WebUIのクローンではないようです${NC}"
  read -p "続行しますか？ (y/n): " CONTINUE
  if [[ $CONTINUE != "y" ]]; then
    echo "セットアップを中止します"
    exit 1
  fi
fi

# GitHubでフォークを作成
echo -e "${YELLOW}GitHubでOpen WebUIをフォークします...${NC}"
echo "ブラウザでhttps://github.com/open-webui/open-webui/fork にアクセスし、フォークを作成してください"
echo "フォークが完了したら何かキーを押してください"
read -n 1 -s

# リモートの設定
echo -e "${YELLOW}リモートリポジトリを設定します...${NC}"
git remote rename origin upstream
git remote add origin "https://github.com/$GITHUB_USERNAME/open-webui.git"
echo -e "${GREEN}リモートリポジトリの設定が完了しました${NC}"
git remote -v

# ブランチの作成
echo -e "${YELLOW}カスタマイズ用のブランチを作成します...${NC}"
git checkout -b custom-microsoft-oauth
echo -e "${GREEN}ブランチの作成が完了しました${NC}"

# 変更をコミット
echo -e "${YELLOW}変更をコミットします...${NC}"
git add src/routes/auth/+page.svelte docker-compose.yaml .env.example README.custom.md setup-fork.sh
git commit -m "Microsoft OAuth専用ログインとCloudflare Tunnelの統合"
echo -e "${GREEN}変更のコミットが完了しました${NC}"

# プッシュの準備
echo -e "${YELLOW}変更をGitHubにプッシュする準備ができました${NC}"
echo "以下のコマンドを実行してプッシュしてください:"
echo -e "${GREEN}git push -u origin custom-microsoft-oauth${NC}"

echo -e "${YELLOW}セットアップが完了しました！${NC}"
echo "フォークリポジトリのURLは: https://github.com/$GITHUB_USERNAME/open-webui"