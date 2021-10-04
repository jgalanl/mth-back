import os
import torch

from flask import Flask, json, request, jsonify
from flask_cors import cross_origin

from http import HTTPStatus

from datetime import datetime

import requests
from bs4 import BeautifulSoup
from markupsafe import escape

from resources.text2tokens import text2tokens
text2tokens = text2tokens()

from transformers import BertForMaskedLM, BertTokenizer

tokenizer = BertTokenizer.from_pretrained("resources/pytorch/", do_lower_case=False)
model = BertForMaskedLM.from_pretrained("resources/pytorch/")
model.eval()

import spacy
from inflector import Inflector, Spanish

nlp = spacy.load('es_core_news_md')
inflector = Inflector(Spanish)

from models.models import Config, Lemma

config = Config()

from flask_mongoengine import MongoEngine

db = MongoEngine()
app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': os.environ['MONGODB_DATABASE'],
    'host': os.environ['MONGODB_HOSTNAME'],
    'username': os.environ['MONGODB_USERNAME'],
    'password': os.environ['MONGODB_PASSWORD'],
    'port': 27017,
    'connect': False
}

db.init_app(app)

@app.route("/", methods=['GET'])
@cross_origin()
def index():
    response = {
        'data': {}
        }
    return response, HTTPStatus.OK


@cross_origin()
@app.route('/api/complex-word', methods=['GET'])
def get_complex_words():
    try:
        text = request.args.get('text')
        flag = request.args.get('flag')
        if text and flag:
            words = list()
            complex_words = list()
            
            sentencelist =  text2tokens.text2sentences(text)
            if flag=='1':
                words = [text2tokens.sentence2tokenseasier(sentence) for sentence in sentencelist]
            elif flag=='0':
                words = [text2tokens.sentence2tokens(sentence) for sentence in sentencelist]
            predictedtags = list()

            if words and words[0]:
                words = [item for item in words if item]
                    
                matrix_deploy = [
                            config.clasificadorobj.getMatrix_Deploy(sentencetags, config.trigrams,config.totalTris, 
                            config.bigrams, config.unigrams, config.totalBis,
                            config.totalUnis, config.uniE2R) for sentencetags in words]
                if flag=='1':
                    predictedtags = [config.clasificadorobj.SVMPredict(rowdeploy) for rowdeploy in matrix_deploy]
                elif flag=='0':
                    predictedtags = [config.clasificadorobj.SVMPredict2(rowdeploy) for rowdeploy in matrix_deploy]
            if flag == '1':
                for j in range(0, len(words)):
                    sentencetags = words[j]
                    for i in range(0, len(sentencetags)):
                        if predictedtags[j][i] == 1:
                            complex_words.append(sentencetags[i])
                        elif predictedtags[j][i] == 0:
                            numsil= config.clasificadorobj.Pyphenobj.getNSyl(sentencetags[i][4])
                            if  numsil >4:
                                complex_words.append(sentencetags[i])
            elif flag == '0':    
                for j in range(0, len(words)):
                    sentencetags = words[j]
                    for i in range(0, len(sentencetags)):
                        if sentencetags[i][4]=='crónicos' or sentencetags[i][4]=='vulnerables':
                            complex_words.append(sentencetags[i])
                        if predictedtags[j][i] == 1:
                            if config.clasificadorobj.getfreqRAE(sentencetags[i][4])==None:
                                complex_words.append(sentencetags[i])
                            elif int(config.clasificadorobj.getfreqRAE(sentencetags[i][4]))>1500:
                                complex_words.append(sentencetags[i]) 

            response = {
                'status': 'success',
                'data': complex_words
            }

            return response, HTTPStatus.OK
            
        else:
            response = {
                'status': 'error',
                'data': {},
                'error': 'Expected text and flags arguments'
            }

            return response, HTTPStatus.BAD_REQUEST
    
    except Exception as e:
        response = {
                'status': 'error',
                'trace': str(e),
                'error': 'Internal server error'
            }

        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@cross_origin()
@app.route('/api/disambiguate', methods=['GET'])
def get_disambiguate():
    try:
        word = request.args.get('word')
        phrase = request.args.get('phrase')
        definition_list = request.args.get('definition_list')

        if word and phrase and definition_list:
            definition_list = json.loads(definition_list)

            phrase = phrase.replace(word, "[MASK]")
            phrase = "[CLS] " + phrase + " [SEP]"

            tokens = tokenizer.tokenize(phrase)
            indexed_tokens = tokenizer.convert_tokens_to_ids(tokens)
            tokens_tensor = torch.tensor([indexed_tokens])
            predictions = model(tokens_tensor)[0]
            midx = tokens.index("[MASK]")
            idxs = torch.argsort(predictions[0,midx], descending=True)
            predicted_token = tokenizer.convert_ids_to_tokens(idxs[:5])

            newpredicted_token=list()
            tokensmlist=list()

            if word in predicted_token:
                predicted_token.remove(word)
            
            other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "tagger"]
            nlp.disable_pipes(*other_pipes)
            for doc in nlp.pipe(predicted_token):
                if len(doc) > 0:
                    if doc[0].pos_=='PROPN' or doc[0].pos_=='NOUN':
                        nword=inflector.pluralize(doc[0].text)
                        newpredicted_token.append(nword)
                newpredicted_token.append(doc)
            doc = nlp(phrase)
            for token in doc:
                if token.pos_ == "NOUN" and token.text!=word:
                    nword=inflector.pluralize(token.text)
                    newpredicted_token.append(nword)
                    newpredicted_token.append(token.text)
                elif token.pos_=="VERB" or token.pos_ == "ADV" or token.pos_ == "PROPN" and token.text!=word:
                    newpredicted_token.append(token.text)
            
            final = ""
            temp = ""
            for meaning in definition_list:
                tokensmlist.append(tokenizer.tokenize(meaning))
                cont=0
                temp=0
                for i in tokensmlist:
                    cont=0
                    for j in newpredicted_token:
                        if j in i:
                            cont=cont+1
                    if cont>temp:
                        final=i
                        temp=cont
            
            if final == "":
                final = definition_list[0]
            else:
                final = " ".join(final)
                final = final.replace(' ##', '').replace(" .", ".").replace(" ,", ",")

            response = {
                'status': 'success',
                'data': final
            }

            return response, HTTPStatus.OK
        
        else:
            response = {
                'status': 'error',
                'data': {},
                'error': 'Expected word, phrase and definition list arguments'
            }

            return response, HTTPStatus.BAD_REQUEST

    except Exception as e:
        response = {
                'status': 'error',
                'trace': str(e),
                'error': 'Internal server error'
            }

        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/synonyms', methods=['GET'])
def get_synonyms():
    try:
        word = request.args.get('word')
        sentencetags = request.args.get('sentencetags')
        
        if word and sentencetags:
            sentencetags = json.loads(sentencetags)

            dis2 = 0
            synonims = list()
            synonimsb = config.diccionario_babel.babelsearch(word)
            synonims_final = list()

            if len(config.dictionario_palabras.SSinonimos(word)):
                if str(word[len(word) - 5:]) == 'mente':
                    stem = word.replace("mente", "")
                    synonims = config.dictionario_palabras.SSinonimos(stem)
                else:
                    stem = config.lematizador.lemmatize(word)
                    synonims = config.dictionario_palabras.SSinonimos(stem)

            if not synonims:
                synonims = config.dictionario_palabras.SSinonimos(word)
                stem = word
        
            synonims_total = list(synonims + synonimsb)
            dic_synonims = dict.fromkeys(synonims_total)

            for candidate in dic_synonims.keys():
                candidatesentencetags = list(sentencetags)
                candidatesentencetags[4] = str(candidate)
                candidatelen = len(candidate)
                wordlen = len(word)
                candidatesentencetags[3] = candidatesentencetags[2] + candidatelen
                candidatesentencetags[1] = str(candidatesentencetags[1])[
                    :candidatesentencetags[2]] + str(candidate) + \
                    candidatesentencetags[1][
                    candidatesentencetags[2] + wordlen:]

                listcandidatesentencetags = list()
                listcandidatesentencetags.append(candidatesentencetags)
        
                # Buscar el sinonimo optimo
                dis1 = config.clasificadorobj.word2vector.similarity(candidate, word)
                window = config.clasificadorobj.getWindow(word, sentencetags[1], sentencetags[2])
                diswindow1 = config.clasificadorobj.word2vector.similarity(window[1], candidate)
                diswindow2 = config.clasificadorobj.word2vector.similarity(window[2], candidate)
                dis3 = dis1 + diswindow1 + diswindow2

                if dis2 < dis3 and word != candidate.lower():
                    dis2 = dis3
                    wordreplace = candidatesentencetags[4]
                    if wordreplace:
                        synonims_final.append(wordreplace)

            # Si se ha encontrado al menos un sinonimo se devuelven los 3 mas significativos            
            if len(synonims_final) > 0:
                response = {
                    'status': 'success',
                    'data': synonims_final[:3]
                }

                return response, HTTPStatus.OK
            # Si no se ha encontrado ningun sinonimo se devuelve una lista con
            # la palabra original
            else:
                synonims_final.append(word)
                response = {
                    'status': 'success',
                    'data': synonims_final
                }

                return response, HTTPStatus.OK

        else:
            response = {
                'status': 'error',
                'data': {},
                'error': 'Expected word, phrase and definition list arguments'
            }

            return response, HTTPStatus.BAD_REQUEST
    
    except Exception as e:
        response = {
                'status': 'error',
                'trace': str(e),
                'error': 'Internal server error'
            }

        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/synonyms/v2', methods=['GET'])
def get_synonyms_v2():
    try:
        word = request.args.get('word')
        sentencetags = request.args.get('sentencetags')

        if word and sentencetags:
            sentencetags = json.loads(sentencetags)
            dicsim={}
            synonims_final = list()
            dicsim2={}
            synonims = list()
            synonimsc=list()
            synonimsb=list()
            stem = config.lematizador.lemmatize(word)
            synonimsb = config.diccionario_babel.babelsearch(word)
            synonimsb+= config.diccionario_babel.babelsearch(stem)
            
            if word.lower() in config.diccionarioparafrases:
                synonimsc=config.diccionarioparafrases[word.lower()]
            else:
                synonimsc.append(word)

            if len(config.dictionario_palabras.SSinonimos(word)):
                synonims = config.dictionario_palabras.SSinonimos(stem)

            if not synonims:
                synonims = config.dictionario_palabras.SSinonimos(word)
                stem = word
            
            synonims_total = list(synonims + synonimsb+synonimsc)
            dic_synonims = dict.fromkeys(synonims_total)

            dic_synonims=text2tokens.eliminarstem(dic_synonims,word.lower())

            for candidate in dic_synonims.keys():
                candidatesentencetags = list(sentencetags)
                candidatesentencetags[4] = str(candidate)
                candidatelen = len(candidate)
                wordlen = len(word)
                candidatesentencetags[3] = candidatesentencetags[2] + candidatelen
                candidatesentencetags[1] = str(candidatesentencetags[1])[:candidatesentencetags[2]] + str(candidate) 
                + candidatesentencetags[1][candidatesentencetags[2] + wordlen:]
                listcandidatesentencetags = list()
                listcandidatesentencetags.append(candidatesentencetags)
                
                # Buscar el sinonimo optimo
                dis1 = config.clasificadorobj.word2vector.similarity(candidate, word)
                window = config.clasificadorobj.getWindowlexical(word, sentencetags[1], sentencetags[2])
                diswindow1 = config.clasificadorobj.word2vector.similarity(window[1], candidate)
                diswindow2 = config.clasificadorobj.word2vector.similarity(window[2], candidate)
                dis3 = dis1 + diswindow1 + diswindow2

                if word != candidate.lower() and candidate.lower()!='':
                    dicsim[candidate]=dis3


            if word.lower() == 'alcance':
                dicsim2={k: v for k, v in sorted(dicsim.items(), key=lambda item: item[1])}
                dicsim2=text2tokens.cleanspecificdic(dicsim2)
            else:
                dicsim=text2tokens.removestemrae(dicsim)
                dicsim2={k: v for k, v in sorted(dicsim.items(), key=lambda item: item[1])}

            # Si se ha encontrado al menos un sinonimo se devuelven los 3 mas significativos            
            if len(dicsim2) > 0:
                synonims_final=list(dicsim2)[-3:]
                if config.clasificadorobj.getfreqRAE(synonims_final[0])==None:
                    synonims_final.insert(0,False)
                    response = {
                        'status': 'success',
                        'data': synonims_final
                    }

                    return response, HTTPStatus.OK

                else:
                    synonims_final.insert(0,True)
                    response = {
                        'status': 'success',
                        'data': synonims_final
                    }

                    return response, HTTPStatus.OK
            # Si no se ha encontrado ningun sinonimo se devuelve una lista con
            # la palabra original
            else:
                synonims_final.append(word)
                response = {
                        'status': 'success',
                        'data': synonims_final
                    }

                return response, HTTPStatus.OK
        
        else:
            response = {
                'status': 'error',
                'data': {},
                'error': 'Expected word, phrase and definition list arguments'
            }

            return response, HTTPStatus.BAD_REQUEST

    except Exception as e:
        response = {
                'status': 'error',
                'trace': str(e),
                'error': 'Internal server error'
            }

        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/lemmatize', methods=['GET'])
def get_lemmatize():
    try:
        word = request.args.get('word')
        if word:
            lemma = text2tokens.lematizar(word)
            response = {
                        'status': 'success',
                        'data': lemma
                    }

            return response, HTTPStatus.OK
        else:
            response = {
                'status': 'error',
                'data': {},
                'error': 'Expected word arguments'
            }

            return response, HTTPStatus.BAD_REQUEST
    
    except Exception as e:
        response = {
                'status': 'error',
                'trace': str(e),
                'error': 'Internal server error'
            }

        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/definition-easy', methods=['GET'])
def get_definition_easy():
    try:
        if request.method == 'GET':
            word = escape(request.args.get('word'))

            definition_list = list()
            page = requests.get(url= 'http://diccionariofacil.org/diccionario/' + word + '.html')
            soup = BeautifulSoup(page.text, 'html.parser')
            error_content = soup.find("div", {"id": "infoBoxArrowError3contendor"})
            if page.status_code == 200 and not error_content:
                definitions_content = soup.findAll(True, {"class":["definicionContent font600", "definicionContent"]})
                for definition_content in definitions_content:
                    definition_list.append(definition_content.text.replace("\n", "")[2:])
                return jsonify(definition_list=definition_list)
            else:
                return jsonify(definition_list=definition_list)
    except Exception as e:
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/lemmas', methods=['GET'])
def get_lemma():
    try:
        skip = request.args.get('skip', default = 0, type = int)
        limit = request.args.get('limit', default = 20, type = int)
        if limit > 20:
            limit = 20

        data = request.get_json()
        lemmas = Lemma.objects().skip(skip).limit(limit)
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
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host="0.0.0.0", port=ENVIRONMENT_PORT)