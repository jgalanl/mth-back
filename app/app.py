import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from flask_pymongo import PyMongo

from models import lemmasrae, Crea

app = Flask(__name__)
# mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/dictionary")
# db = mongodb_client.db

app.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

# app.config['MONGODB_SETTINGS'] = {
#     'db': 'dictionary',
#     'alias':'default'
# }

mongo = PyMongo(app)
db = mongo.db


@app.route('/', methods=['GET'])
def root():
    return jsonify(
        status=True,
        message='Welcome to the Dockerized Flask MongoDB app!'
    )

@app.route('/lemma/<word>')
def lemma(word):
    print(word)
    todos = lemmasrae.objects(lemma=word)
    
    # todos = db.lemmasRae.find_one({"lemma": word})


    return jsonify(todos), 200

@app.route('/freq/<word>')
def freq(word):
    # result = LemmasRae.objects.filter(lemma=word)

    todos = Crea.objects(lemma=word)

    return jsonify(todos)


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)