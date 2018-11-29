from flask import Flask
from .api.view import api
from .view import home


def get_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.register_blueprint(api)
    app.register_blueprint(home)
    return app
