import time
import os
import subprocess
import config
import requests
from operator import methodcaller
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from bodyparts import camera
from face_rec_service import FaceRecService
from logger import logger


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
        msg = "Prediction mode on!! I cam predict faced of '{}'".format("','".join(set(self.facerec_service.names)))
        bot.send_message(chat_id=update.message.chat_id, text=msg)

    def takepic_command(self, bot, update, args):
        cam = camera.Camera()
        cam.open_eyes()
        img = cam.get_frame(save=True)
        cam.close_eyes()
        bot.send_photo(update.message.chat_id, open(img), 'here you go!')
        logger.warn('deleting %s', img)
        os.remove(img)

    def move_command(self, bot, update, args):
        logger.info('move %s' % args)
        responses = [requests.get('http://localhost:8080/api/wheels/%s' % direction) for direction in args]
        if all(res.ok for res in responses):
            bot.send_message(chat_id=update.message.chat_id, text='moved')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='could not move %s' % ', '.join([d for d, res in zip(args, responses) if not res.ok]))

    def _convert_vid(self, filepath):
        newfilepath = os.path.splitext(filepath)[0] + '.mp4'
        command = "MP4Box -add {} {}".format(filepath, newfilepath)
        logger.info(command)
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            logger.error('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
        else:
            return newfilepath

    def recordvid_command(self, bot, update, args):
        logger.info('record command %s', args)
        secs = 10
        res = (512, 288)
        if args:
            try:
                secs = int(args[0])
            except Exception as ex:
                logger.warn(str(ex))
            try:
                res = map(int, args[1:3])
            except Exception as ex:
                logger.warn(str(ex))

        logger.info('creating camera')
        cam = camera.Camera()
        logger.info('opening camera')
        cam.open_eyes()
        logger.info('camera warmed up')
        filepath = './tmp/vid/%s.h264' % str(int(time.time()))
        logger.info('starting to record at %s', filepath)
        cam.start_recording(filepath, res)
        time.sleep(secs)
        cam.stop_recording()
        logger.info('recording complete')
        cam.close_eyes()
        logger.info('camera closed')
        # convert video
        logger.info('converting video to mp4')
        newfilepath = self._convert_vid(filepath)
        logger.warn('deleting %s', filepath)
        os.remove(filepath)
        logger.info('sending message')
        bot.send_video(chat_id=update.message.chat_id, video=open(newfilepath, 'rb'), supports_streaming=True)
        logger.warn('deleting %s', newfilepath)
        os.remove(newfilepath)

    def _get_biggest_photo_size(self, photos):
        photos.sort(key=methodcaller('__getitem__', 'file_size'))
        return photos[-1]

    def photo_msg(self, bot, update):
        photo = self._get_biggest_photo_size(update.message.photo)
        filename = str(time.time()) + config.IMG_EXTN
        filepath = os.path.join('.', 'tmp', filename)
        photo.get_file().download(filepath)
        face_filenames = self.facerec_service.extract_faces(filepath)
        logger.info('faces %s', face_filenames)
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

        takepic_handler = CommandHandler('photo', self.takepic_command, pass_args=True)
        self.dispatcher.add_handler(takepic_handler)

        record_handler = CommandHandler('video', self.recordvid_command, pass_args=True)
        self.dispatcher.add_handler(record_handler)

        move_handler = CommandHandler('move', self.move_command, pass_args=True)
        self.dispatcher.add_handler(move_handler)

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
