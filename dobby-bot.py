import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from operator import methodcaller
import time
import os
import cv2
import config
import cloudinary
import cloudinary.uploader
import re
import numpy as np
import requests
import zipfile
import StringIO


logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)
logger = logging.getLogger('dobby')


class FaceRepo(object):

    def __init__(self, base_path='tmp'):
        if not config.CLOUDINARY_URL:
            raise Exception('set CLOUDINARY_URL environment variable before creating FaceRepo instances')
        self.base_path = base_path
        self.face_data_dir = 'face-data'
        self.img_extn = '.jpg'

    def download_all(self):
        zip_file_url = cloudinary.utils.download_zip_url(prefixes='/')
        logger.info("source zip url: %s", zip_file_url)
        r = requests.get(zip_file_url, stream=True)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall(path='tmp/face-data/')

    def upload(self, imagepath, name):
        if not name:
            name = 'unknown'
        folder = '-'.join(re.split(r'\s+', name.lower()))
        if not os.path.exists(imagepath):
            logger.error('%s does not exists', imagepath)
            return
        res = cloudinary.uploader.upload(imagepath, folder=folder)
        logger.debug(res)

    def _folder_to_name(self, foldername):
        if foldername:
            return foldername.replace('-', ' ')

    def _name_to_folder(self, name):
        if name:
            return name.lower().replace(' ', '-')

    def _capitalize(self, name):
        words = name.split(' ')
        words = [chr(ord(word[0]) - 32) + word[1:] for word in words]
        return ' '.join(words)

    def get_faces_and_names(self):
        # Assuming every folder under tmp/ represents a person name seperated by `-`
        # All files inside ./tmp/firstname-secondname/* is a face image of the person with that name
        self.download_all()
        # parse the folder
        faces, labels = [], []
        logger.info(self.base_path)
        logger.info(self.face_data_dir)
        dirname = os.path.join(self.base_path, self.face_data_dir)
        logger.info("%s %s", dirname, os.listdir(dirname))
        if not os.path.exists(dirname):
            raise Exception('%s does not exists' % dirname)
        subjectsdir = [dname for dname in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, dname))]
        logger.info("subjectsdir %s", subjectsdir)
        names = [self._folder_to_name(subject) for subject in subjectsdir]
        logger.info("names %s", names)
        names = [self._capitalize(name) for name in names]
        logger.info("names %s", names)
        for folder, name in zip(subjectsdir, names):
            img_files = os.listdir(os.path.join(dirname, folder))
            logger.info("img_files %s", img_files)
            img_files = [img for img in img_files if img.endswith('%s' % self.img_extn)]
            logger.info("img_files %s", img_files)
            for img_file in img_files:
                img_path = os.path.join(dirname, folder, img_file)
                face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if face_img is not None:
                    faces.append(face_img)
                    labels.append(name)
        logger.info("faces loded are %s", set(labels))
        return faces, labels


class FaceRecService(object):

    def __init__(self):
        self.f_cascade = cv2.CascadeClassifier(config.CASCADE_FILE)
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_repo = FaceRepo()
        self.train()

    def train(self):
        faces, self.names = self.face_repo.get_faces_and_names()
        lables = np.array(list(range(len(self.names))))
        self.face_recognizer.train(faces, lables)

    def labelToName(self, label):
        if label < len(self.names):
            return self.names[label]

    def extract_faces(self, filename):
        img_copy = cv2.imread(filename)
        img_gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
        cordinates = self.f_cascade.detectMultiScale(img_gray,
                                                     scaleFactor=1.1,
                                                     minNeighbors=3)
        if len(cordinates) == 0:
            return None, None

        faces_images = [img_gray[y:y + w, x:x + h] for (x, y, w, h) in cordinates]
        face_filenames = [self._save_face_img(face) for face in faces_images]
        os.remove(filename)
        return face_filenames

    def _save_face_img(self, img):
        filename = str(time.time()) + config.IMG_EXTN
        filepath = os.path.join('.', 'tmp', 'faces', filename)
        cv2.imwrite(filepath, img)
        time.sleep(0.25)
        return filepath

    def predict(self, faceimg):
        # predict the image using our face recognizer
        prediction = self.face_recognizer.predict(cv2.imread(faceimg, cv2.IMREAD_GRAYSCALE))
        if prediction:
            lable, confidence = prediction
            name = self.labelToName(lable)
            logger.info("prediction %s with %s confidence", name, confidence)
            return name


class TelegramBot(object):
    fileid_filepath_map = {}

    def __init__(self):
        token = config.TELEGRAM_BOT_ACCESS_TOKEN
        if not token:
            raise Exception("set TELEGRAM_BOT_ACCESS_TOKEN before creating TelegramBot instances")
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.learn = True
        self.facerec_service = FaceRecService()

    def start_command(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Hi! I'm Dobby I'm in leaning mode!")

    def learn_command(self, bot, update, args):
        self.learn = True
        bot.send_message(chat_id=update.message.chat_id, text="Learning mode on!")

    def predict_command(self, bot, update, args):
        self.learn = False
        self.facerec_service = FaceRecService()
        bot.send_message(chat_id=update.message.chat_id, text="Prediction mode on!")

    def _get_biggest_photo_size(self, photos):
        photos.sort(key=methodcaller('__getitem__', 'file_size'))
        return photos[-1]

    def photo_msg(self, bot, update):
        photo = self._get_biggest_photo_size(update.message.photo)
        filename = str(time.time()) + config.IMG_EXTN
        filepath = os.path.join('.', 'tmp', filename)
        photo.get_file().download(filepath)
        face_filenames = self.facerec_service.extract_faces(filepath)
        for facefilepath in face_filenames:
            if self.learn:
                message = bot.send_photo(update.message.chat_id, open(facefilepath), "Who is this?")
                photo = self._get_biggest_photo_size(message.photo)
                if photo:
                    logger.info("%s %s", photo.file_id, facefilepath)
                self.fileid_filepath_map[photo.file_id] = facefilepath
            else:
                name = self.facerec_service.predict(facefilepath)
                if name:
                    bot.send_photo(update.message.chat_id, open(facefilepath), name)
                else:
                    bot.send_photo(update.message.chat_id, open(facefilepath), "unknown")

    def reply_msg(self, bot, update):
        if update.message.reply_to_message.photo:
            photo = self._get_biggest_photo_size(update.message.reply_to_message.photo)
            logger.info("%s %s", photo.file_id, update.message.text)
            facefilepath = self.fileid_filepath_map.get(photo.file_id)
            if facefilepath:
                self.facerec_service.face_repo.upload(facefilepath, update.message.text)
                logger.info("added another face for %s", update.message.text)

    def register_handlers(self):
        start_handler = CommandHandler('start', self.start_command)
        self.dispatcher.add_handler(start_handler)

        learn_handler = CommandHandler('learn', self.learn_command, pass_args=True)
        self.dispatcher.add_handler(learn_handler)

        predict_handler = CommandHandler('predict', self.predict_command, pass_args=True)
        self.dispatcher.add_handler(predict_handler)

        photo_handler = MessageHandler(Filters.photo, self.photo_msg)
        self.dispatcher.add_handler(photo_handler)

        reply_handler = MessageHandler(Filters.reply, self.reply_msg)
        self.dispatcher.add_handler(reply_handler)

    def start(self):
        self.register_handlers()
        try:
            self.updater.start_polling()
            self.updater.idle()
        except KeyboardInterrupt:
            self.updater.stop()


if __name__ == '__main__':
    TelegramBot().start()
