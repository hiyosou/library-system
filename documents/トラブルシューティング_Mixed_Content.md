# Mixed Content エラーのトラブルシューティング

## 問題: HTTPSページからHTTPリソースを読み込もうとしてブロックされる

### エラーメッセージ
```
Mixed Content: The page at 'https://library.nu-tf-lab.jp/' was loaded over HTTPS, 
but requested an insecure resource 'http://library.nu-tf-lab.jp/books/'. 
This request has been blocked; the content must be served over HTTPS.
```

## 原因と解決方法

### 1. 環境変数 `APP_BASE_URL` が設定されていない

**確認方法:**
```bash
# Proxmoxサーバーで確認
docker compose exec app printenv | grep APP_BASE_URL

# または、ブラウザで確認
https://library.nu-tf-lab.jp/debug/env
```

**解決方法:**
```bash
# /root/library-system/.env ファイルを編集
nano .env

# 以下を追加（HTTPSのURLを指定すること！）
APP_BASE_URL=https://library.nu-tf-lab.jp

# コンテナを再起動
docker compose restart app
```

### 2. HTMLに環境変数が反映されていない

**確認方法:**
ブラウザで開発者ツール（F12）を開き、以下をコンソールで実行:
```javascript
console.log(APP_BASE_URL);
```

**期待する結果:** `https://library.nu-tf-lab.jp`
**NGの結果:** `http://localhost:5000` または `{{ app_base_url }}`（テンプレートがレンダリングされていない）

**解決方法:**
```bash
# コンテナを再ビルド
docker compose down
docker compose up -d --build
```

### 3. Nginxが `X-Forwarded-Proto` ヘッダーを送信していない

**確認方法:**
```bash
# デバッグエンドポイントで確認
curl https://library.nu-tf-lab.jp/debug/env
```

`X-Forwarded-Proto`が`https`になっているか確認。

**解決方法:**
Nginxの設定に以下を追加:
```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header X-Forwarded-Proto $scheme;  # これを追加
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Nginx設定を再読み込み:
```bash
nginx -t  # 設定ファイルの文法チェック
systemctl reload nginx  # または nginx -s reload
```

### 4. ブラウザキャッシュの問題

**解決方法:**
- `Ctrl + F5` または `Shift + F5` でハードリロード
- ブラウザの開発者ツールで「キャッシュを無効にする」を有効化
- シークレット/プライベートモードで開く

### 5. アプリケーションログの確認

```bash
# リアルタイムでログを確認
docker compose logs -f app

# 起動時のログを確認
docker compose logs app | grep INFO
```

以下のログが表示されるはず:
```
[INFO] APP_BASE_URL is set to: https://library.nu-tf-lab.jp
[INFO] Flask Environment: production
[INFO] SESSION_COOKIE_SECURE: True
```

## 完全な設定チェックリスト

### Proxmoxサーバー側

- [ ] `.env`ファイルに`APP_BASE_URL=https://library.nu-tf-lab.jp`が設定されている
- [ ] `docker compose restart app`を実行済み
- [ ] `docker compose logs app`でエラーがない

### Nginx側

- [ ] `proxy_set_header X-Forwarded-Proto $scheme;`が設定されている
- [ ] SSL証明書が正しく設定されている
- [ ] HTTPからHTTPSへのリダイレクトが設定されている
- [ ] `nginx -t`でエラーがない

### ブラウザ側

- [ ] キャッシュをクリア済み
- [ ] 開発者ツールでネットワークタブを確認
- [ ] すべてのリクエストが`https://`で始まっている

## デバッグコマンド集

```bash
# 環境変数を確認
docker compose exec app env | grep APP_BASE_URL

# HTMLのレンダリング結果を確認
curl -s https://library.nu-tf-lab.jp/ | grep "APP_BASE_URL"

# ヘッダー情報を確認
curl -I https://library.nu-tf-lab.jp/

# デバッグエンドポイントで詳細確認
curl https://library.nu-tf-lab.jp/debug/env | jq

# コンテナのログを確認
docker compose logs app --tail=100

# Nginxの設定を確認
nginx -T | grep -A 10 "server_name library.nu-tf-lab.jp"
```

## よくある間違い

1. `.env`ファイルを編集したが、コンテナを再起動していない
2. `APP_BASE_URL`が`http://`で始まっている（HTTPSにすること！）
3. Nginxの設定を変更したが、リロードしていない
4. ブラウザのキャッシュが残っている
5. 開発用の`.env.example`を使っている（本番用の設定を使うこと）

## まだ解決しない場合

1. コンテナを完全に再ビルド:
```bash
docker compose down -v
docker compose up -d --build
```

2. Nginxを再起動:
```bash
systemctl restart nginx
```

3. サポートに連絡する際は以下の情報を提供:
   - `docker compose logs app`の出力
   - `curl https://library.nu-tf-lab.jp/debug/env`の出力
   - ブラウザのコンソールのエラーメッセージ
   - Nginxのログ: `/var/log/nginx/error.log`
