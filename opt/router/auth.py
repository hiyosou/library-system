"""OAuth認証ルーター"""
from flask import Blueprint, request, redirect, session, jsonify, render_template, url_for
import secrets
from service.oauth import OAuthService

bp = Blueprint('auth', __name__)


@bp.route('/login')
def login():
    """ログインページを表示、またはOAuth認証フローを開始する"""
    # stateパラメータを生成してセッションに保存（CSRF対策）
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # 認証URLを生成してリダイレクト
    auth_url = OAuthService.get_authorization_url(state)
    return redirect(auth_url)


@bp.route('/callback')
def callback():
    """OAuth認証サーバーからのコールバック"""
    # エラーチェック
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description', 'Unknown error')
        return render_template('error.html', error=error, error_description=error_description), 400
    
    # codeとstateを取得
    code = request.args.get('code')
    state = request.args.get('state')
    
    # stateの検証（CSRF対策）
    if not state or state != session.get('oauth_state'):
        return jsonify({'error': 'Invalid state parameter'}), 400
    
    # stateを削除
    session.pop('oauth_state', None)
    
    if not code:
        return jsonify({'error': 'Authorization code not found'}), 400
    
    # コードをトークンに交換
    token_data = OAuthService.exchange_code_for_token(code)
    if not token_data:
        return jsonify({'error': 'Failed to exchange code for token'}), 500
    
    # アクセストークンを取得
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    
    if not access_token:
        return jsonify({'error': 'Access token not found in response'}), 500
    
    # ユーザー情報を取得
    user_info = OAuthService.get_user_info(access_token)
    if not user_info:
        return jsonify({'error': 'Failed to get user info'}), 500
    
    # セッションに保存
    session['logged_in'] = True
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token
    session['user_info'] = user_info
    
    # indexページにリダイレクト
    return redirect(url_for('index_alias'))


@bp.route('/logout')
def logout():
    """ログアウト"""
    # トークンを無効化
    access_token = session.get('access_token')
    if access_token:
        OAuthService.revoke_token(access_token, 'access')
    
    refresh_token = session.get('refresh_token')
    if refresh_token:
        OAuthService.revoke_token(refresh_token, 'refresh')
    
    # セッションをクリア
    session.clear()
    
    return redirect(url_for('login'))


@bp.route('/user')
def user():
    """現在のユーザー情報を取得"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_info = session.get('user_info')
    if not user_info:
        return jsonify({'error': 'User info not found'}), 404
    
    return jsonify(user_info)


@bp.route('/validate')
def validate():
    """トークンの有効性を検証"""
    if not session.get('logged_in'):
        return jsonify({'valid': False, 'error': 'Not authenticated'}), 401
    
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'valid': False, 'error': 'Access token not found'}), 404
    
    # トークンを検証
    validation_result = OAuthService.validate_token(access_token)
    if not validation_result:
        # トークンが無効な場合、リフレッシュを試みる
        refresh_token = session.get('refresh_token')
        if refresh_token:
            token_data = OAuthService.refresh_token(refresh_token)
            if token_data:
                # 新しいトークンをセッションに保存
                session['access_token'] = token_data.get('access_token')
                return jsonify({'valid': True, 'refreshed': True})
        
        # リフレッシュも失敗した場合
        session.clear()
        return jsonify({'valid': False, 'error': 'Token expired and refresh failed'}), 401
    
    return jsonify({'valid': True, 'data': validation_result})
