"""FlaskアプリがSQLAlchemyを使えるようにするための初期化"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()#インスタンスの生成


def init_db(app):
    db.init_app(app)#SQLAlchemyをappで使う準備
