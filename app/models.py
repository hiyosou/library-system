from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'  # データベース上のテーブル名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自動採番される整数ID
    title = db.Column(db.String(100), nullable=False)  # 本のタイトル
    author = db.Column(db.String(50), nullable=False)  # 作者名

    def __repr__(self):
        return f'<Book {self.id}: {self.title} by {self.author}>'
class User(db.Model):
    __tablename__ = 'users'
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)