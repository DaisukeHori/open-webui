#!/bin/bash
# ビルドとデプロイを最適化するスクリプト

# 不要なファイルを削除してディスク容量を確保
echo "ディスク容量を確保しています..."
sudo apt-get clean
sudo apt-get autoremove -y
rm -rf ~/.cache/pip/* 2>/dev/null
docker system prune -f

# メモリの最適化
echo "スワップを設定しています..."
# スワップが存在しない場合は作成
if [ $(sudo swapon --show | wc -l) -eq 0 ]; then
    echo "スワップを作成しています..."
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "/swapfile swap swap defaults 0 0" | sudo tee -a /etc/fstab
else
    echo "スワップが既に存在します"
fi

# メモリ使用量の最適化設定
echo "メモリ使用量を最適化しています..."
export NODE_OPTIONS="--max-old-space-size=2048"
export DOCKER_BUILDKIT=1

# ビルドの段階的実行
echo "Docker Composeビルドを実行します..."
docker-compose build --no-cache open-webui

echo "ビルド完了後、コンテナを起動しています..."
docker-compose up -d

echo "デプロイが完了しました！"
echo "ステータス確認:"
docker-compose ps