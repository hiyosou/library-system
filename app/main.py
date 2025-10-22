from flask import Flask, request, jsonify
from book import Book, books

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()

    book_id = len(books) + 1

    new_book = Book(id=book_id, title=data.get('title'), author=data.get('author'))
    books.append(new_book)

    return jsonify({"message": "本の登録に成功しました。", 
                    "book": {"id": new_book.id, 
                             "title": new_book.title, 
                             "author": new_book.author}}), 201
