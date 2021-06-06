from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_mongoengine import MongoEngine

from flask_pymongo import PyMongo

from models import lemmasrae, Crea

app = Flask(__name__)
# mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/dictionary")
# db = mongodb_client.db

app.config['MONGODB_SETTINGS'] = {
    'db': 'dictionary',
    'alias':'default'
}

db = MongoEngine()
db.init_app(app)


@app.route('/', methods=['GET'])
def root():
    
    return {}, 200

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


app.run()