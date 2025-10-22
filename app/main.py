from flask import Flask, request, jsonify
from books import Book, books
from database import init_db
def create_app():
    app = Flask(__name__)#Flaskアプリの生成
    app.config.from_object('flask_sample.config.Config')
    
    init_db(app)

    return app

app = create_app()

@app.route('/books', methods=['POST']) #書籍登録(POST)
def add_book():
    data = request.get_json()

    book_id = len(books) + 1

    new_book = Book(id=book_id, title=data.get('title'), author=data.get('author'))
    books.append(new_book)

    return jsonify({"message": "本の登録に成功しました。", 
                    "book": {"id": new_book.id, 
                             "title": new_book.title, 
                             "author": new_book.author}}), 201

@app.route('/books/<int:book_id>', methods=['PUT']) #書籍情報の更新(PUT)
def update_book(book_id):
    data = request.get_json()

    book_to_update = next((book for book in books if book.id == book_id), None)
    
    if not book_to_update:
        return jsonify({"message": "書籍が見つかりません。"}), 404

    if 'title' in data:
        book_to_update.title = data['title']
    if 'author' in data:
        book_to_update.author = data['author']

    return jsonify({"message": "情報を更新しました。",
                    "book": {"id": book_to_update.id,
                             "title": book_to_update.title,
                             "author": book_to_update.author}}), 200

@app.route('/books/<int:book_id>', methods=['PATCH']) #書籍の貸出・返却(PATCH)
def update_borrowing_status(book_id):
    book = next((b for b in books if b.id == book_id), None)
    
    if not book:
        return jsonify({"message": "書籍が見つかりません。"}), 404
    
    data = request.get_json()
    
    if 'action' not in data:
        return jsonify({"message": "アクションが指定されていません。"}), 400
    
    if data['action'] == "borrow":
        if book.is_borrowed:
            return jsonify({"message": "この書籍はすでに貸し出されています。"}), 409
        book.is_borrowed = True
        return jsonify({"message": "貸し出しました。"}), 200
    
    elif data['action'] == "return":
        if not book.is_borrowed:
            return jsonify({"message": "この書籍は貸し出されていません。"}), 409
        book.is_borrowed = False
        return jsonify({"message": "返却しました。"}), 200
    
    else:
        return jsonify({"message": "不明なアクションが指定されました。"}), 400
@app.route('/books', methods=['GET']) #書籍一覧の取得(GET)
def get_books():
    title_query = request.args.get('title', None, type=str)
    author_query = request.args.get('author', None, type=str)
    fields = request.args.get('fields', None, type=str)

    filtered_books = books
    if title_query:
        filtered_books = [b for b in filtered_books if title_query.lower() in b.title.lower()]
    if author_query:
        filtered_books = [b for b in filtered_books if author_query.lower() in b.author.lower()]

    if not filtered_books:
        return jsonify({"message": "該当する書籍が見つかりません。"}), 404

    response_books = []
    for book in filtered_books:
        status_msg = "貸出中" if book.is_borrowed else "利用可能"
        book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "loanStatus": status_msg
        }
        
        if fields:
            fields_list = fields.split(',')
            book_data = {key: book_data[key] for key in fields_list if key in book_data}
        
        response_books.append(book_data)

    response = {"books": response_books}
    if len(response_books) > 1:
        response["count"] = len(response_books)

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)