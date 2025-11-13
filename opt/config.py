"""OAuth設定ファイル"""
import os

# 認証サーバーの設定
# ブラウザからのアクセス用（リダイレクト先）
AUTH_SERVER_BASE_URL_BROWSER = os.getenv('AUTH_SERVER_BASE_URL_BROWSER', 'http://localhost:3030')

# サーバー間通信用（Dockerコンテナ内からのアクセス）
AUTH_SERVER_BASE_URL_SERVER = os.getenv('AUTH_SERVER_BASE_URL_SERVER', 'http://host.docker.internal:3030')

# 後方互換性のため（未設定の場合はBROWSERを使用）
AUTH_SERVER_BASE_URL = AUTH_SERVER_BASE_URL_BROWSER

# OAuthクライアント設定
OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID', '')
OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET', '')
OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:5000/auth/callback')

# APIキー（サーバー間通信用）
API_KEY = os.getenv('API_KEY', '')

# スコープ
OAUTH_SCOPE = os.getenv('OAUTH_SCOPE', 'read:profile')

# セッション設定
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
