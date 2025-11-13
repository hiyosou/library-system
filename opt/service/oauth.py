"""OAuth認証サービス"""
import requests
from typing import Optional, Dict, Any
from config import (
    AUTH_SERVER_BASE_URL_BROWSER,
    AUTH_SERVER_BASE_URL_SERVER,
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    OAUTH_REDIRECT_URI,
    API_KEY,
    OAUTH_SCOPE
)


class OAuthService:
    """OAuth認証サービスクラス"""

    @staticmethod
    def get_authorization_url(state: str) -> str:
        """
        認証URLを生成する（ブラウザがアクセスするURL）
        
        Args:
            state: CSRF対策用のstate値
            
        Returns:
            認証サーバーの認証URL
        """
        params = {
            'client_id': OAUTH_CLIENT_ID,
            'redirect_uri': OAUTH_REDIRECT_URI,
            'state': state,
            'scope': OAUTH_SCOPE,
            'response_type': 'code'
        }

        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        # ブラウザからアクセスするのでBROWSER用のURLを使用
        return f"{AUTH_SERVER_BASE_URL_BROWSER}/oauth/client/authorize?{query_string}"

    @staticmethod
    def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
        """
        認証コードをアクセストークンに交換する（サーバー間通信）
        
        Args:
            code: 認証コード
            
        Returns:
            トークン情報の辞書、失敗時はNone
        """
        try:
            response = requests.post(
                f"{AUTH_SERVER_BASE_URL_SERVER}/oauth/client/token",
                json={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'client_id': OAUTH_CLIENT_ID,
                    'client_secret': OAUTH_CLIENT_SECRET,
                    'redirect_uri': OAUTH_REDIRECT_URI
                },
                timeout=10
            )

            if response.status_code == 200:
                res = response.json()
                return res
            else:
                print(f"Token exchange failed: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Token exchange error: {e}")
            return None

    @staticmethod
    def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """
        アクセストークンを使ってユーザー情報を取得する（サーバー間通信）
        
        Args:
            access_token: アクセストークン
            
        Returns:
            ユーザー情報の辞書、失敗時はNone
        """
        try:
            response = requests.get(
                f"{AUTH_SERVER_BASE_URL_SERVER}/oauth/client/userinfo",
                headers={
                    'Authorization': f'Bearer {access_token}'
                },
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Get user info failed: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Get user info error: {e}")
            return None

    @staticmethod
    def refresh_token(refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        リフレッシュトークンを使って新しいアクセストークンを取得する（サーバー間通信）
        
        Args:
            refresh_token: リフレッシュトークン
            
        Returns:
            新しいトークン情報の辞書、失敗時はNone
        """
        try:
            response = requests.post(
                f"{AUTH_SERVER_BASE_URL_SERVER}/oauth/client/token",
                json={
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                    'client_id': OAUTH_CLIENT_ID,
                    'client_secret': OAUTH_CLIENT_SECRET
                },
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Token refresh failed: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Token refresh error: {e}")
            return None

    @staticmethod
    def validate_token(access_token: str) -> Optional[Dict[str, Any]]:
        """
        アクセストークンの有効性を検証する（サーバー間通信）
        
        Args:
            access_token: アクセストークン
            
        Returns:
            検証結果の辞書、失敗時はNone
        """
        try:
            response = requests.post(
                f"{AUTH_SERVER_BASE_URL_SERVER}/oauth/app-server/validate",
                headers={
                    'X-API-Key': API_KEY
                },
                json={
                    'accessToken': access_token
                },
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Token validation failed: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Token validation error: {e}")
            return None

    @staticmethod
    def revoke_token(token: str, token_type: str = 'access') -> bool:
        """
        トークンを無効化する（サーバー間通信）
        
        Args:
            token: 無効化するトークン
            token_type: トークンタイプ ('access' or 'refresh')
            
        Returns:
            成功時はTrue、失敗時はFalse
        """
        try:
            response = requests.post(
                f"{AUTH_SERVER_BASE_URL_SERVER}/oauth/app-server/revoke",
                headers={
                    'X-API-Key': API_KEY
                },
                json={
                    'token': token,
                    'tokenType': token_type
                },
                timeout=10
            )

            return response.status_code == 204

        except requests.exceptions.RequestException as e:
            print(f"Token revocation error: {e}")
            return False
