from flask import Flask, request, jsonify,render_template
# from books import Book, books
from router import book
import os
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
from models import db

# === データベースファイルの保存先を指定 ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # main.pyがあるディレクトリの絶対パス
DB_BOOK_PATH = os.path.join(BASE_DIR,'DB','books.db')            # DBファイルパス
DB_USER_PATH = os.path.join(BASE_DIR,'DB','user.db')            # DBファイルパス


# === SQLAlchemyの設定 ===
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_BOOK_PATH}'#デフォルトのデータベース(本の情報用)
app.config['SQLALCHEMY_BINDS'] = {'users': f'sqlite:///{DB_USER_PATH}', }#ユーザーデータ用のデータベース
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # 初期化

from models import Book

with app.app_context():
    db.create_all()  # データベースとテーブルを作成

app.register_blueprint(book.bp,url_prefix="/books")#ルート設定の分割

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
