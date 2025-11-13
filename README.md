# library-system

図書管理システム - OAuth 2.0認証対応

## 概要

このシステムは、LabNexus認証サーバーとOAuth 2.0 Authorization Code Flowで連携する図書管理システムです。

## 機能

- OAuth 2.0認証によるログイン/ログアウト
- 書籍の登録・編集・削除
- 書籍の検索

## セットアップ

### 1. 環境変数の設定

`.env.example`ファイルをコピーして`.env`ファイルを作成し、必要な値を設定してください。

```bash
cp .env.example .env
```

`.env`ファイルの設定項目:

- `AUTH_SERVER_BASE_URL`: 認証サーバーのベースURL（例: http://localhost:3030）
- `OAUTH_CLIENT_ID`: 認証サーバーから発行されたクライアントID
- `OAUTH_CLIENT_SECRET`: 認証サーバーから発行されたクライアントシークレット
- `OAUTH_REDIRECT_URI`: コールバックURI（例: http://localhost:5000/auth/callback）
- `API_KEY`: サーバー間通信用のAPIキー（認証サーバーのサービスアカウントから取得）
- `OAUTH_SCOPE`: 必要なスコープ（例: read:profile）
- `SECRET_KEY`: Flaskセッション用のシークレットキー（本番環境では必ず変更）

### 2. Dockerでの起動

```bash
docker compose up -d --build
```

### 3. ローカルでの起動（開発用）

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# アプリケーションの起動
cd opt
python main.py
```

アプリケーションは `http://localhost:5000` で起動します。

## OAuth 2.0フロー

詳細は `documents/簡易OAuth.md` を参照してください。

### 認証フロー

1. ユーザーがログインボタンをクリック
2. 認証サーバーの認証ページにリダイレクト
3. ユーザーがログイン（email/password）
4. 認証コードが発行され、コールバックURIにリダイレクト
5. アプリサーバーが認証コードをアクセストークンに交換
6. アクセストークンを使ってユーザー情報を取得
7. セッションを確立してログイン完了

### エンドポイント

- `GET /login` - ログイン（OAuth認証フローを開始）
- `GET /auth/callback` - OAuth認証サーバーからのコールバック
- `GET /auth/logout` - ログアウト
- `GET /auth/user` - 現在のユーザー情報取得
- `GET /auth/validate` - トークンの有効性検証

## 参考

第4回のQiita記事: https://qiita.com/kazuki_tachikawa/items/7dab01ac2ea08b85fb15

