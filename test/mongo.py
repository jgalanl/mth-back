from flask import Flask, json, request, jsonify
from flask_cors import cross_origin
# from flask_pymongo import PyMongo
from http import HTTPStatus
# from bson.json_util import dumps
from mongoengine import connect, Document, StringField, DecimalField

from marshmallow import Schema, fields

app = Flask(__name__)

connect('test', host='127.0.0.1', port=27017)

class Lemma(Document):
    lemma = StringField()
    prev_lemma = StringField()
    next_lemma = StringField()
    frecuencia = DecimalField()

    def update(self, newdata):
        for key,value in newdata.items():
            setattr(self,key, value)
        self.save()

    @property
    def serialize(self):
        return {
            "lemma": self.lemma,
            "frecuencia": float(self.frecuencia) if self.frecuencia else None,
            "prev_lemma": self.prev_lemma,
            "next_lemma": self.next_lemma
        }


@app.route("/", methods=['GET'])
@cross_origin()
def index():
    response = {
        'data': {}
        }
    return response, HTTPStatus.OK

@app.route("/api/complex-word", methods=['GET'])
@cross_origin()
def get_complex_words():
    response = {
        'data': {}
        }
    return response, HTTPStatus.OK

    
@app.route("/api/disambiguate", methods=['GET'])
@cross_origin()
def get_disambiguate():
    response = {
        'data': {}
        }
    return response, HTTPStatus.OK


@app.route("/api/synonyms", methods=['GET'])
@cross_origin()
def get_synonyms():
    response = {
        'data': {}
        }
    return response, HTTPStatus.OK      


@app.route("/api/lemmatize", methods=['GET'])
@cross_origin()
def get_lemmatize():
    response = {
        'data': {}
        }
    return response, HTTPStatus.OK      


@app.route('/api/lemmas', methods=['GET'])
def get_lemma():
    try:
        lemmas = Lemma.objects()
        response = {
                        'status': 'success',
                        'data': [lemma.serialize for lemma in lemmas]
                    }
        return response, HTTPStatus.OK

    except Exception as e:
        response = {
                'status': 'error',
                'trace': str(e),
                'error': 'Internal server error'
            }

        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/lemmas/<string:lemma>', methods=['GET'])
def get_lemma_by_id(lemma):
    try:
        # Comprobar si el lemma existe
        lemma = lemma.lower()
        lemma_obj = Lemma.objects(lemma=lemma).first()
        if lemma_obj:
            response = {
                'status': 'success',
                'data': lemma_obj.serialize
                }
            return response, HTTPStatus.OK
        else:
            response = {
                'status': 'error',
                'message': 'Resource does not exist'
            }
            return response, HTTPStatus.NOT_FOUND

    except Exception as e:
        response = {
                'status': 'error',
                'trace': str(e),
                'error': 'Internal server error'
            }

        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/lemmas', methods=['POST'])
def post_lemma():
    try:
        # Check if request is correct
        data = request.get_json(force=True)
        if data and data['lemma']:
            # Comprobar si el lemma existe
            find = Lemma.objects(lemma=data['lemma']).first()
            if not find:
                data['date_insert'] = datetime.utcnow()
                lemma = Lemma(**data)
                lemma.save()

                response = {
                    'status': 'success',
                    'data': {}
                }
                return response, HTTPStatus.CREATED
            else:
                response = {
                    'status': 'error',
                    'message': 'Resource already exists'
                }
                return response, HTTPStatus.CONFLICT
        else:
            response = {
                'status': 'error',
                'message': 'Resource does not exist'
            }
            return response, HTTPStatus.NOT_FOUND
    
    except Exception as e:
        response = {
                'status': 'error',
                'trace': str(e),
                'error': 'Internal server error'
            }

        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/lemmas/<string:lemma>', methods=['PUT'])
def put_lemma(lemma):
    data = request.get_json(force=True)

    lemma_obj = Lemma.objects(lemma=lemma).first()
    if lemma_obj:
        lemma_obj.update(data)
        response = {
            'status': 'success',
            'data': {}
        }
        return response, HTTPStatus.OK
    else:
        response = {
            'status': 'error',
            'message': 'Resource does not exist'
        }
        return response, HTTPStatus.NOT_FOUND


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)