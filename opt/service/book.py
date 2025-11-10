from flask import Flask, request, jsonify,render_template
from models import db,Book

cbooks=[]

def add_book():#本の登録機能
    data = request.get_json()


    new_book = Book(title=data.get('title'), author=data.get('author'))#本のインスタンス作成
    db.session.add(new_book)#データベースへの追加
    db.session.commit()

    return jsonify({"message": "本の登録に成功しました。", 
                    "book": {"id": new_book.id, 
                             "title": new_book.title, 
                             "author": new_book.author}}), 201

def update_book(book_id):#本の情報更新機能
   
    data = request.get_json()

    # データベースから該当する本を取得
    book_to_update = Book.query.get(book_id)

    if not book_to_update:
        return jsonify({"message": "書籍が見つかりません。"}), 404

    # 更新するフィールドがリクエストデータに含まれている場合に更新
    if 'title' in data:
        book_to_update.title = data['title']
    if 'author' in data:
        book_to_update.author = data['author']

    # データベースに変更を保存
    db.session.commit()


    return jsonify({"message": "情報を更新しました。",
                    "book": {"id": book_to_update.id,
                             "title": book_to_update.title,
                             "author": book_to_update.author}}), 200

def delete_book(book_id):
    try:
        book_to_delete = Book.query.get(book_id)

        if not book_to_delete:
            return jsonify({"message": "書籍が見つかりません。"}), 404

        db.session.delete(book_to_delete)
        db.session.commit()

        return jsonify({"message": "書籍を削除しました。"}), 200

    except Exception as e:
        db.session.rollback()  # エラー時にロールバック
        return jsonify({"message": "削除中にエラーが発生しました。", "error": str(e)}), 500

# 書籍一覧取得機能
def get_books():
    books = Book.query.all()
    books_list = [
        {"id": book.id, "title": book.title, "author": book.author}
        for book in books
    ]
    return jsonify(books_list)