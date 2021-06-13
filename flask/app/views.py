from http import HTTPStatus
from app import app

@app.route("/")
def index():
    return "Hello from flask"

@app.route("/", methods='POST')
def post():
    response = {
        'data': 'post example'
    }
    return response, HTTPStatus.OK