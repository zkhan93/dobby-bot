from flask import Blueprint, request

home = Blueprint('home', 'homebp', url_prefix='/')


@home.route('/')
def index():
    print(request.data)
    print(request.json)
    print(request.args)
    return 'Working!!'
