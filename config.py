import os


TELEGRAM_BOT_ACCESS_TOKEN = os.environ.get('TELEGRAM_BOT_ACCESS_TOKEN')
TELEGRAM_BASE_URL = 'https://api.telegram.org/'

TELEGRAM_METHOD_BASE_URL = '{baseurl}bot{token}'.format(baseurl=TELEGRAM_BASE_URL,
                                                        token=TELEGRAM_BOT_ACCESS_TOKEN)

TELEGRAM_FILE_BASE_URL = '{baseurl}file/bot{token}'.format(baseurl=TELEGRAM_BASE_URL,
                                                           token=TELEGRAM_BOT_ACCESS_TOKEN)
CASCADE_FILE = 'data/cascades/lbpcascade_frontalface.xml'

IMG_EXTN = '.jpg'

CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
