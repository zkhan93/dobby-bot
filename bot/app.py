from flask import Flask
from .api.view import api
from .view import home
import os
import sys
import logging
import cv2
import multiprocessing
import cloudinary

#face_recognizer = cv2.face.LBPHFaceRecognizer_create()
f_cascade = None


def download_images():
    cloudinary_url = os.environ.get('CLOUDINARY_URL')


def get_app():
    global f_cascade
    app = Flask(__name__)
    app.config.from_object('bot.config.Config')

    cascade_filepath = app.config.get('CASCADE_FILE')
    if not os.path.exists(cascade_filepath):
        raise Exception('path %s does not exists' % cascade_filepath)
    f_cascade = cv2.CascadeClassifier(cascade_filepath)

    process = multiprocessing.Process(target=download_images)
    process.start()

    app.register_blueprint(api)
    app.register_blueprint(home)

    if 'DYNO' in os.environ:
        app.logger.addHandler(logging.StreamHandler(sys.stdout))
        app.logger.setLevel(logging.INFO)

    return app
