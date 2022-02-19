from flask import Flask, make_response, request, jsonify, render_template
from flask_mongoengine import MongoEngine
import chatbot_fonctions as chat
from mongoengine import IntField
from mongoengine import StringField
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

database_name = "API"
DB_URI = "mongodb+srv://shadow:IoWeSNE9oFAdvgV4@cluster0.w2fqm.mongodb.net/API?retryWrites=true&w=majority"

app.config["MONGODB_HOST"] = DB_URI
db = MongoEngine()
db.init_app(app)


class Book(db.Document):
    book_id = IntField()
    name = StringField()
    author = StringField()

    def to_json(self):
        return {
            "book_id": self.book_id,
            "name": self.name,
            "author": self.author}


class Chat(db.Document):
    chat_id = IntField()
    question = StringField()
    answer = StringField()

    def to_json(self):
        return {

            "question": self.question,
            "answer": self.answer}


@app.route('/')
def hello_world():  # put application's code here

    return render_template('index.html')


@app.route('/api/dbPopulate', methods=['POST'])
def db_populate():
    chat = Chat(question="what is your name ?", answer="I am an intelligent atrifical chatbot")
    chat.save()
    return make_response("", 201)


@app.route('/api/books', methods=['POST', 'GET'])
def api_books():
    if request.method == "GET":
        books = []
        for book in Book.objects:
            books.append(book)
        return make_response(jsonify(books), 200)
    elif request.method == "POST":
        '''
        Sample Request Body
        {
        "book_id" : 1,
        "name" : "Game of thrones",
        "author" : "George Martin luther king"
        }

        '''
        content = request.json
        book = Book(book_id=content['book_id'], name=content['name'], author=content['author'])
        book.save()
        return make_response("", 201)


@app.route('/api/books/<book_id>', methods=['GET', 'PUT', 'DELETE'])
def api_each_book(book_id):
    if request.method == "GET":
        book_obj = Book.objects(book_id=book_id).first()
        if book_obj:
            return make_response(jsonify(book_obj.to_json()), 200)
        else:
            return make_response("", 404)


    elif request.method == "PUT":
        '''
        Sample Request Body
        {
        "book_id" : 1,
        "name" : "Game of thrones",
        "author" : "George Martin luther king"
        }

        '''
        content = request.json
        book_obj = Book.objects(book_id=book_id).first()
        book_obj.update(author=content['author'], name=content['name'])
        return make_response("", 204)

    elif request.method == "DELETE":
        book_obj = Book.objects(book_id=book_id).first()
        book_obj.delete()
        return make_response("")


def chatbot_response(msg):
    res = chat.get_response(msg)
    return res


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)


if __name__ == '__main__':
    app.run()
