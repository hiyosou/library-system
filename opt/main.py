from flask import Flask, request, jsonify,render_template,redirect,url_for,session
# from books import Book, books
from router import book, auth
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

app = Flask(__name__)
from models import db
from flask_cors import CORS
from config import SECRET_KEY

CORS(app)

# HTTPSリダイレクト用のミドルウェア
@app.before_request
def redirect_to_https():
    """本番環境でHTTPSを強制する"""
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# セッション設定
app.secret_key = SECRET_KEY

# HTTPSでのセキュアなセッションクッキー設定
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPSのみでクッキーを送信
app.config['SESSION_COOKIE_HTTPONLY'] = True  # JavaScriptからのアクセスを防ぐ
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF対策

# === MySQLデータベースの設定 ===
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'library_db')
MYSQL_USER = os.getenv('MYSQL_USER', 'library_user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'library_pass')

# === SQLAlchemyの設定 ===
# pymysqlを使用したMySQL接続文字列
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # 初期化

from models import Book

with app.app_context():
    db.create_all()  # データベースとテーブルを作成

app.register_blueprint(book.bp,url_prefix="/books")#ルート設定の分割
app.register_blueprint(auth.bp,url_prefix="/auth")#OAuth認証ルート

# アプリケーションのベースURL
APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:5000')

@app.route('/')
def index():
    return render_template('search.html', app_base_url=APP_BASE_URL)
@app.route("/search")
def search_page():
    return render_template("search.html", app_base_url=APP_BASE_URL)
@app.route("/login")
def login():
    # OAuth認証フローにリダイレクト
    return redirect(url_for("auth.login"))
@app.route("/index")
def index_alias():
    # ログインしていなければ login.html にリダイレクト
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html", app_base_url=APP_BASE_URL)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
