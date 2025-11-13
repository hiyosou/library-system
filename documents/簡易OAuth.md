# OAuth 2.0 フロー解説

本システムでは、OAuth 2.0 の Authorization Code Flow を基にした簡易的な認証・認可の仕組みを実装しています。このドキュメントでは、システム固有の簡略化や共通化について解説します。

## 概要

LabNexus の OAuth 2.0 実装は以下の特徴を持ちます：

- **簡略化されたフロー**: 標準的な OAuth 2.0 を研究室管理システム向けに簡略化
- **3 つのアクターモデル**: エンドユーザー（メンバー）、クライアント（アプリサーバー）、認証サーバー（LabNexus API）
- **サービスアカウントとの統合**: OAuth クライアントは必ずサービスアカウントに紐づく
- **API Key ベースのサービス間認証**: アプリサーバーから認証サーバーへのリクエストは API Key で認証

## システムアーキテクチャ

```mermaid
graph TB
    User[エンドユーザー<br/>メンバー<br/>ブラウザ]
    AppServer[アプリサーバー<br/>OAuth クライアント<br/>Web App]
    AuthServer[認証サーバー<br/>LabNexus API<br/>OAuth 2.0]

    User -->|① 認証要求| AppServer
    AppServer -->|② /oauth/client/authorize<br/>③ /oauth/client/token<br/>④ /oauth/client/userinfo| AuthServer
    AppServer -.->|⑤ /oauth/app-server/validate<br/>⑥ /oauth/app-server/revoke<br/>サーバー間通信 API Key| AuthServer

    style User fill:#e1f5ff
    style AppServer fill:#fff4e1
    style AuthServer fill:#e8f5e9
```

## OAuth 2.0 フロー

### フロー 1: Authorization Code Flow（クライアントからのリクエスト）

エンドユーザーがアプリケーションサーバーにログインする際のフローです。

```mermaid
sequenceDiagram
    participant Browser as ブラウザ<br/>(User)
    participant AppServer as アプリ<br/>サーバー
    participant AuthServer as 認証<br/>サーバー

    Browser->>AppServer: 1. ログインボタン
    AppServer->>Browser: 2. 認証要求リダイレクト<br/>(client_id, redirect_uri, state, scope)
    Browser->>AuthServer: 3. GET /oauth/client/authorize?...
    AuthServer->>Browser: 4. ログインページ表示<br/>(未認証の場合)
    Browser->>AuthServer: 5. ログイン情報送信<br/>(email, password)
    Note over AuthServer: 6. 認証成功<br/>→ authorization_code 生成
    AuthServer->>Browser: 7. リダイレクト<br/>(redirect_uri?code=xxx&state=xxx)
    Browser->>AppServer: 8. コールバック (code, state)
    AppServer->>AuthServer: 9. POST /oauth/client/token<br/>Body: {<br/>  grant_type: "authorization_code",<br/>  code: "xxx",<br/>  client_id: "...",<br/>  client_secret: "...",<br/>  redirect_uri: "..."<br/>}
    Note over AuthServer: 10. code 検証<br/>→ access_token 発行
    AuthServer->>AppServer: 11. トークンレスポンス<br/>{<br/>  access_token: "...",<br/>  token_type: "Bearer",<br/>  expires_in: 3600,<br/>  refresh_token: "...",<br/>  scope: "..."<br/>}
    AppServer->>Browser: 12. ログイン成功<br/>(セッション確立)
```

#### シーケンスの詳細

**ステップ 1-2: ログイン開始**

- ユーザーがアプリサーバーのログインボタンをクリック
- アプリサーバーは認証サーバーの `/oauth/client/authorize` へリダイレクト

**ステップ 3-5: 認証**

- 認証サーバーはユーザーが未認証の場合、ログインページを表示
- ユーザーは email と password でログイン

**ステップ 6-7: 認証コード発行**

- 認証成功時、認証サーバーは `authorization_code` を生成して DB に保存
- `redirect_uri` に code と state を付けてリダイレクト

**ステップ 8-11: トークン交換**

- アプリサーバーは code を受け取り、`/oauth/client/token` へリクエスト
- `client_id` と `client_secret` で OAuth クライアント自身を認証
- 認証サーバーは code を検証し、`access_token` と `refresh_token` を発行

**ステップ 12: ログイン完了**

- アプリサーバーはトークンを保存し、ユーザーセッションを確立

### フロー 2: ユーザー情報取得（クライアントからのリクエスト）

アクセストークンを使ってユーザー情報を取得します。

```mermaid
sequenceDiagram
    participant AppServer as アプリ<br/>サーバー
    participant AuthServer as 認証<br/>サーバー

    AppServer->>AuthServer: 1. GET /oauth/client/userinfo<br/>Authorization: Bearer {access_token}
    Note over AuthServer: 2. トークン検証<br/>→ member 情報取得
    AuthServer->>AppServer: 3. ユーザー情報レスポンス<br/>{<br/>  id: "...",<br/>  email: "...",<br/>  name: "...",<br/>  scope: "..."<br/>}
```

**ポイント**:

- アクセストークンは Bearer Token として Authorization ヘッダーで送信
- scope に応じて返却される情報が変わる（実装依存）

### フロー 3: トークンリフレッシュ（クライアントからのリクエスト）

アクセストークンの期限が切れた際に、リフレッシュトークンで新しいアクセストークンを取得します。

```mermaid
sequenceDiagram
    participant AppServer as アプリ<br/>サーバー
    participant AuthServer as 認証<br/>サーバー

    AppServer->>AuthServer: 1. POST /oauth/client/token<br/>Body: {<br/>  grant_type: "refresh_token",<br/>  refresh_token: "...",<br/>  client_id: "...",<br/>  client_secret: "..."<br/>}
    Note over AuthServer: 2. refresh_token 検証<br/>→ 新しい access_token 発行
    AuthServer->>AppServer: 3. トークンレスポンス<br/>{<br/>  access_token: "...",<br/>  token_type: "Bearer",<br/>  expires_in: 3600<br/>}
```

### フロー 4: トークン検証（アプリサーバーからのリクエスト）

**システム固有の特徴**: アプリサーバーが認証サーバーに直接トークンの有効性を確認するエンドポイントを提供しています。

```mermaid
sequenceDiagram
    participant AppServer as アプリ<br/>サーバー
    participant AuthServer as 認証<br/>サーバー

    AppServer->>AuthServer: 1. POST /oauth/app-server/validate<br/>Header: X-API-Key: {api_key}<br/>Body: {<br/>  accessToken: "..."<br/>}
    Note over AuthServer: 2. API Key 検証<br/>→ access_token 検証
    AuthServer->>AppServer: 3. 検証結果<br/>{<br/>  valid: true,<br/>  memberId: "...",<br/>  email: "...",<br/>  exp: 1234567890<br/>}
```

**ポイント**:

- **サーバー間通信**: API Key で認証（`X-API-Key` ヘッダー）
- OAuth クライアントに紐づくサービスアカウントの API Key を使用
- トークンの有効性だけでなく、ユーザー情報も返却

### フロー 5: トークン無効化（アプリサーバーからのリクエスト）

強制ログアウトなどでトークンを無効化します。

```mermaid
sequenceDiagram
    participant AppServer as アプリ<br/>サーバー
    participant AuthServer as 認証<br/>サーバー

    AppServer->>AuthServer: 1. POST /oauth/app-server/revoke<br/>Header: X-API-Key: {api_key}<br/>Body: {<br/>  token: "...",<br/>  tokenType: "access"<br/>}
    Note over AuthServer: 2. API Key 検証<br/>→ トークン無効化<br/>(is_revoked = true)
    AuthServer->>AppServer: 3. 204 No Content
```
