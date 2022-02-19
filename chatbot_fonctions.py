import pandas as pd

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split as tts
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder as LE
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

import nltk
from nltk.corpus import stopwords


def get_database():
    from pymongo import MongoClient
    import pymongo

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://shadow:IoWeSNE9oFAdvgV4@cluster0.w2fqm.mongodb.net/API?retryWrites=true&w" \
                        "=majority "

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['API']


dbname = get_database()

collection_name = dbname["chat"]

data = pd.DataFrame.from_records(collection_name.find())

questions = data['Question'].values
questions
stop_words = set(stopwords.words('english'))
print(stop_words)


def cleanup(sentence):
    word_tok = nltk.word_tokenize(sentence)
    stemmed_words = [w for w in word_tok if not w in stop_words]
    print(stemmed_words)

    # stemmed_words = [stemmer.stem(w) for w in word_tok]
    return ' '.join(stemmed_words)


le = LE()

tfv = TfidfVectorizer(min_df=1, stop_words='english')

questions = data['Question'].values

X = []

for question in questions:
    X.append(cleanup(question))
tfv.fit(X)
le.fit(data['Class'])

X = tfv.transform(X)

y = le.transform(data['Class'])

trainx, testx, trainy, testy = tts(X, y, test_size=.3, random_state=42)

model = SVC(kernel='linear')  # using SVC i think using SGD will give better result but not far apart from each other
model.fit(trainx, trainy)

# model = SGDClassifier(loss="hinge", penalty="l2", max_iter=5)

class_ = le.inverse_transform(model.predict(X))

print("SVC:", model.score(testx, testy))


def get_max5(arr):
    ixarr = []
    for ix, el in enumerate(arr):
        ixarr.append((el, ix))

    ixarr.sort()
    ixs = []
    for i in ixarr[-5:]:
        ixs.append(i[1])

    return ixs[::-1]


def get_response(usrText):
    while True:

        if usrText.lower() == "bye":
            return "Bye"

        GREETING_INPUTS = ["hello", "hi", "greetings", "sup", "what's up", "hey", "hiii", "hii", "yo"]

        a = [x.lower() for x in GREETING_INPUTS]

        sd = ["Thanks", "Welcome"]

        d = [x.lower() for x in sd]

        am = ["OK"]

        c = [x.lower() for x in am]

        ty = ["getting"]
        r = [x.lower() for x in ty]

        t_usr = tfv.transform([cleanup(usrText.strip().lower())])
        class_ = le.inverse_transform(model.predict(t_usr))
        print(class_)

        questionset = data[data['Class'].values == class_]
        print(questionset)
        cos_sims = []
        for question in questionset['Question']:
            sims = cosine_similarity(tfv.transform([question]), t_usr)

            cos_sims.append(sims)

        ind = cos_sims.index(max(cos_sims))

        b = [questionset.index[ind]]

        if usrText.lower() in a:
            return ("Hi, I'm Personal Chatbot!\U0001F60A")

        if usrText.lower() in c:
            return "Ok...Alright!\U0001F64C"

        if usrText.lower() in d:
            return ("My pleasure! \U0001F607")

        if max(cos_sims) > [[0.]]:
            a = data['Answer'][questionset.index[ind]] + "   "
            return a


        elif max(cos_sims) == [[0.]]:
            msg = get_response2(usrText)
            return msg


def get_response2(usr):
    if usr.lower() == "bye":
        return "Thanks for having conversation! \U0001F60E"

    GREETING_INPUTS = ["hello", "hi", "greetings", "sup", "what's up", "hey", "hii", "hiii", "hiiiii", "yo",
                       "Hey there"]

    a = [x.lower() for x in GREETING_INPUTS]

    sd = ["Thanks", "Welcome"]

    d = [x.lower() for x in sd]

    am = ["OK"]

    c = [x.lower() for x in am]

    t_usr = tfv.transform([cleanup(usr.strip().lower())])
    class_ = le.inverse_transform(model.predict(t_usr))

    questionset = data[data['Class'].values == class_]

    cos_sims = []
    for question in questionset['Question']:
        sims = cosine_similarity(tfv.transform([question]), t_usr)

        cos_sims.append(sims)
        print(max(cos_sims))

    ind = cos_sims.index(max(cos_sims))

    b = [questionset.index[ind]]

    if usr.lower() in a:
        return ("you can ask me questions related to: Accounts, Investments, Funds, etc.")

    if usr.lower() in c:
        return " Cool! \U0001f604"

    if usr.lower() in d:
        return ("\U0001F44D")

    if max(cos_sims) == [[0.]]:
        return "I'm not able to solve this question at this moment. You can call to customer support 1860 999 9999 \U0001F615"

    if max(cos_sims) > [[0.]]:
        inds = get_max5(cos_sims)
        print(inds)

        b = "1)" + data['Question'][questionset.index[0]]
        c = "\n2)" + data['Question'][questionset.index[1]]
        d = "\n3)" + data['Question'][questionset.index[2]]
        e = "\n4)" + data['Question'][questionset.index[3]]
        f = "\n5)" + data['Question'][questionset.index[4]]

        return "Following are the Recommended Questions:" + b + c + d + e + f
