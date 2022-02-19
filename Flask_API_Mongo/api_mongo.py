from flask import Flask
from flask_mongoengine import  MongoEngine

app = Flask(__name__)
db = MongoEngine()
db.init_app(app)
database_name = "API"
DB_URI ="mongodb+srv://shadow:Mouhamed123456@cluster0.qowi2.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app.config["MONGODB_HOST"] = DB_URI
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello my bro!'

if __name__ == '__main__':
    app.run()
