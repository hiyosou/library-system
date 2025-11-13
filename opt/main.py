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

# セッション設定
app.secret_key = SECRET_KEY

# === データベースファイルの保存先を指定 ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # main.pyがあるディレクトリの絶対パス
DB_DIR = os.path.join(BASE_DIR, 'DB')  # DBディレクトリパス

# DBディレクトリが存在しない場合は作成
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_BOOK_PATH = os.path.join(DB_DIR, 'books.db')            # DBファイルパス
DB_USER_PATH = os.path.join(DB_DIR, 'user.db')            # DBファイルパス


# === SQLAlchemyの設定 ===
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_BOOK_PATH}'#デフォルトのデータベース(本の情報用)
app.config['SQLALCHEMY_BINDS'] = {'users': f'sqlite:///{DB_USER_PATH}', }#ユーザーデータ用のデータベース
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # 初期化

from models import Book

with app.app_context():
    db.create_all()  # データベースとテーブルを作成

app.register_blueprint(book.bp,url_prefix="/books")#ルート設定の分割
app.register_blueprint(auth.bp,url_prefix="/auth")#OAuth認証ルート

@app.route('/')
def index():
    return render_template('search.html')
@app.route("/search")
def search_page():
    return render_template("search.html")
@app.route("/login")
def login():
    # OAuth認証フローにリダイレクト
    return redirect(url_for("auth.login"))
@app.route("/index")
def index_alias():
    # ログインしていなければ login.html にリダイレクト
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
