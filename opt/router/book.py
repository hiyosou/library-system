from flask import Blueprint
from flask import Flask, request, jsonify,render_template
from service import book 

bp=Blueprint('books',__name__,url_prefix="")#ルーティングを行うbpオブジェクト

# 書籍一覧取得エンドポイント
@bp.route('/', methods=['GET'])
def get_books():
    return book.get_books()

@bp.route('/', methods=['POST'])
def add_book():
    return book.add_book()

@bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    return book.update_book(book_id)

@bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    return book.delete_book(book_id)