from http import HTTPStatus
from flask_cors import cross_origin
from app import app

@app.route("/", methods=['GET'])
@cross_origin()
def index():
    return "Hello from flask"

@app.route("/", methods=['POST'])
@cross_origin()
def post():
    response = {
        'data': 'post example'
    }
    return response, HTTPStatus.OK