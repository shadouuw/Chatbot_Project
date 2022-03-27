# import required module
import os

os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
import vlc
import bcrypt
import detectlanguage
import pygame
import speech_recognition as s_r
from deep_translator import GoogleTranslator
from flask import Flask, make_response, request, jsonify, render_template, session
from flask_mongoengine import MongoEngine
from gtts import gTTS
from mongoengine import IntField
from mongoengine import StringField
from pyglet.media import load, Player

import chatbot_fonctions as chat


def text_to_speech(text, language):
    mytext = "bonjour je suis ton assitant personelle comment puis je vous aidez"


detectlanguage.configuration.api_key = "d7f3b6137274f895cc6fd059befdd9b2"

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, root_path=dir_path)

database_name = "API"
DB_URI = "mongodb+srv://shadow:IoWeSNE9oFAdvgV4@cluster0.w2fqm.mongodb.net/API?retryWrites=true&w=majority"

app.config["MONGODB_HOST"] = DB_URI
db = MongoEngine()
db.init_app(app)


class Disscussion(db.Document):
    client_question = StringField()
    chatbot_answer = StringField()
    is_correct_answer = IntField()

    def to_json(self):
        return {
            "client_question": self.client_question,
            "chatbot_answer": self.chatbot_answer,
            "is_correct_answer": self.is_correct_answer
        }


class User(db.Document):
    email = StringField()
    password = StringField()
    role = StringField()

    def to_json(self):
        return {
            "email": self.email,
            "password": self.password,
            "role": self.role

        }


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

    return render_template('chat.html')


@app.route('/d')
def hello_worldd():  # put application's code here

    return render_template('test.html')


@app.route('/hello2')
def hello_world2():  # put application's code here

    return render_template('index2.html')


# exemple d'ajout
@app.route('/api/dbPopulate', methods=['POST'])
def db_populate():
    chat = User(email="hamma", password="123456", role="role")
    chat.save()
    return make_response("", 201)


# petit exemple de crud
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
    if detectlanguage.simple_detect(msg) == "fr" or detectlanguage.simple_detect(msg) == "ar":
        translated = GoogleTranslator(source='auto', target='en').translate(msg)
        res = chat.get_response(translated)
        res = GoogleTranslator(source='auto', target=detectlanguage.simple_detect(msg)).translate(res)
        dis = Disscussion(client_question=msg, chatbot_answer=res, is_correct_answer=-1)
        dis.save()

    return res


def chatbot_response_lang(msg, lang):
    translated = GoogleTranslator(source='auto', target='en').translate(msg)
    res = chat.get_response(translated)
    res = GoogleTranslator(source='auto', target=lang).translate(res)

    return res


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)


@app.route("/count_answer")
def get_stat2():
    n = chat.data["Question"].count()
    n2 = chat.data["Answer"].count()

    return str(n) + "." + str(n2)


lang = "en"


@app.route("/correct_answer")
def get_corrects():
    n = 0
    n2 = 0

    for i in chat.data2["is_correct_answer"]:
        if i == -1:
            n = n + 1
        else:
            n2 = n2 + 1

    return str(n) + "." + str(n2)


@app.route("/get_arab")
def get_arab():
    media.stop()
    try:
        import os
        os.remove("1.mp3")
    except:
        print("no file ")

    userText = ""
    print(s_r.__version__)  # just to print the version not required
    r = s_r.Recognizer()
    my_mic = s_r.Microphone(device_index=1)  # my device index is 1, you have to put your device index
    with my_mic as source:
        print("Say now!!!!")
        r.adjust_for_ambient_noise(source)  # reduce noise
        audio = r.listen(source)  # take voice input from the microphone
    userText = r.recognize_google(audio, language="ar")  # to print voice into text
    userText2 = chatbot_response_lang(userText, "ar")

    myobj = gTTS(text=userText2, lang="ar", slow=False)
    myobj.save("1.mp3")

    mp3 = vlc.Media("1.mp3")
    media.set_media(mp3)

    media.play()


media = vlc.MediaPlayer()
vlc.libvlc_media_player_set_rate(rate=1.2, p_mi=media)


@app.route("/get_english")
def get_english():
    media.stop()

    try:
        import os
        os.remove("1.mp3")
    except:
        print("no file ")
    userText = ""
    print(s_r.__version__)  # just to print the version not required
    r = s_r.Recognizer()
    my_mic = s_r.Microphone(device_index=1)  # my device index is 1, you have to put your device index
    with my_mic as source:
        print("Say now!!!!")
        r.adjust_for_ambient_noise(source)  # reduce noise
        audio = r.listen(source)  # take voice input from the microphone
    userText = r.recognize_google(audio, language="en")  # to print voice into text
    userText2 = chatbot_response(userText)

    myobj = gTTS(text=userText2, lang="en", slow=False)

    myobj.save("1.mp3")

    mp3 = vlc.Media("1.mp3")
    media.set_media(mp3)

    media.play()

    return userText


p = pygame.mixer
p.init()


@app.route("/get_fr")
def get_fr():
    media.stop()
    try:

        import os
        os.remove("1.mp3")
    except:
        print("no file ")
    pygame.mixer.stop()
    r = s_r.Recognizer()
    my_mic = s_r.Microphone(device_index=1)  # my device index is 1, you have to put your device index
    with my_mic as source:
        print("Say now!!!!")
        r.adjust_for_ambient_noise(source)  # reduce noise
        audio = r.listen(source)  # take voice input from the microphone
    userText = r.recognize_google(audio, language="fr")  # to print voice into text
    userText2 = chatbot_response_lang(userText, "fr")
    myobj = gTTS(text=userText2, lang="fr", slow=False, tld='com')

    myobj.save("1.mp3")

    mp3 = vlc.Media("1.mp3")
    media.set_media(mp3)

    media.play()


@app.route('/login')
def login():
    email = request.args.get('username')
    password = request.args.get('pass')
    login_user = User.objects(email=email).first()

    if login_user:

        if bcrypt.hashpw(password.encode('utf-8'), login_user['password'].encode('utf-8')) == \
                login_user[
                    'password'].encode('utf-8'):
            return "1"

    return "0"


@app.route("/register1")
def register1():
    users = db.Document()

    # existing_user = users.find_one({'name': request.form['username']})
    login_user = User.objects(email="hamma").first()
    passs = "1234567"
    hashpass = bcrypt.hashpw(passs.encode('utf-8'), bcrypt.gensalt())
    password_hash = hashpass.decode('utf8')
    chat = User(email="hamma3", password=password_hash, role="employee")
    chat.save()
    session['username'] = "hamma"

    return render_template('login.html')


if __name__ == '__main__':
    app.run()
