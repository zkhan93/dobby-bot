from flask import Blueprint, request

api = Blueprint('api', 'api_bp', url_prefix='/api')


@api.route('/')
def home():
    print(request.data)
    print(request.json)
    print(request.args)
    return 'Working!!'
