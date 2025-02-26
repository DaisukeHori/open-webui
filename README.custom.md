# カスタマイズされたOpen WebUI

このリポジトリは[Open WebUI](https://github.com/open-webui/open-webui)をフォークし、以下の機能を追加したものです：

1. **Cloudflare Tunnelによる安全なアクセス**
   - SSL証明書と独自ドメインを自動的に設定
   - 外部からのアクセスをCloudflare経由で安全に提供

2. **Microsoft Entra ID (Azure AD) によるシングルサインオン**
   - Microsoft アカウントのみでログイン可能
   - 通常のユーザー名/パスワード認証を無効化

## セットアップ手順

### 1. 前提条件

- Dockerとdocker-composeがインストールされていること
- Cloudflareアカウント
- Microsoft Azure アカウント（Entra ID / Azure ADの設定用）

### 2. Microsoft OAuth設定

1. [Azure Portal](https://portal.azure.com/)にアクセス
2. 「Azure Active Directory」→「アプリの登録」→「新規登録」を選択
3. アプリケーション名を入力（例：「Open WebUI」）
4. サポートされているアカウントの種類を選択（通常は「この組織ディレクトリのみ」）
5. リダイレクトURIを設定：
   - 種類：「Web」
   - URL：`https://your-domain.example.com/oauth/microsoft/callback`
   （※ `your-domain.example.com` は後でCloudflareで設定するドメイン）
6. 「登録」をクリック
7. 登録後、以下の情報をメモ：
   - アプリケーション（クライアント）ID → `MICROSOFT_CLIENT_ID`
   - ディレクトリ（テナント）ID → `MICROSOFT_CLIENT_TENANT_ID`
8. 「証明書とシークレット」→「新しいクライアントシークレット」を選択
9. 説明と有効期限を入力し、「追加」をクリック
10. 生成されたシークレット値をメモ → `MICROSOFT_CLIENT_SECRET`

### 3. Cloudflare Tunnel設定

1. [Cloudflare Dashboard](https://dash.cloudflare.com/)にアクセス
2. 使用するドメインを選択
3. 左メニューから「Zero Trust」→「Access」→「Tunnels」を選択
4. 「Create a tunnel」をクリック
5. トンネル名を入力（例：「open-webui」）
6. 「Next」をクリック
7. 「Docker」タブを選択し、表示されるトークンをメモ → `TUNNEL_TOKEN`
8. 「Next」をクリック
9. 「Public Hostname」を設定：
   - ドメイン：`your-domain.example.com`
   - サービス：`http://localhost:8080`
   - 「Save」をクリック

### 4. 環境変数の設定

1. `.env.example`ファイルを`.env`にコピー
2. `.env`ファイルを編集し、以下の値を設定：
   - `MICROSOFT_CLIENT_ID`
   - `MICROSOFT_CLIENT_SECRET`
   - `MICROSOFT_CLIENT_TENANT_ID`
   - `TUNNEL_TOKEN`

```bash
cp .env.example .env
nano .env  # または任意のテキストエディタで編集
```

### 5. 起動

```bash
docker-compose up -d
```

### 6. アクセス

ブラウザで `https://your-domain.example.com` にアクセスすると、Microsoft アカウントでのログイン画面が表示されます。

## 注意事項

- 最初のログインユーザーが管理者権限を持ちます
- すべてのデータはコンテナボリュームに保存されます
- Cloudflare Tunnelを使用しているため、ポートの開放は不要です

## トラブルシューティング

### ログの確認

```bash
# Open WebUIのログを確認
docker logs open-webui

# Cloudflare Tunnelのログを確認
docker logs cloudflared
```

### 再起動

```bash
docker-compose restart
```

### 完全な再構築

```bash
docker-compose down
docker-compose up -d --build