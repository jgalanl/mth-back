import os

from flask import Flask

app = Flask(__name__)

from http import HTTPStatus
from flask import request
from flask_cors import cross_origin

import requests
from bs4 import BeautifulSoup
from markupsafe import escape
from flask import jsonify

from resources.text2tokens import text2tokens

text2tokens = text2tokens()


from models.models import Config

config = Config()

@app.route("/", methods=['GET'])
@cross_origin()
def index():
    response = {
        'data': {}
        }
    return response, HTTPStatus.OK


@app.route('/api/complex-word', methods=['GET'])
def get_complex_words():
    if request.method == 'GET':
        text = request.args.get('text')
        flag = request.args.get('flag')

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
        if flag=='1':
            for j in range(0, len(words)):
                sentencetags = words[j]
                for i in range(0, len(sentencetags)):
                    if predictedtags[j][i] == 1:
                        complex_words.append(sentencetags[i])
                    elif predictedtags[j][i] == 0:
                        numsil= config.clasificadorobj.Pyphenobj.getNSyl(sentencetags[i][4])
                        if  numsil >4:
                            complex_words.append(sentencetags[i])
        elif flag=='0':    
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
                                

        return jsonify(result=complex_words)


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


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host="0.0.0.0", port=ENVIRONMENT_PORT)