import os


class Config(object):
    TELEGRAM_BOT_ACCESS_TOKEN = os.environ.get('TELEGRAM_BOT_ACCESS_TOKEN')
    TELEGRAM_BASE_URL = 'https://api.telegram.org/'
    TELEGRAM_FILE_INFO_URL = '{baseurl}bot{token}/getFile'.format(baseurl=TELEGRAM_BASE_URL,
                                                                  token=TELEGRAM_BOT_ACCESS_TOKEN)
    TELEGRAM_FILE_URL = '{baseurl}file/bot{token}/'.format(baseurl=TELEGRAM_BASE_URL,
                                                           token=TELEGRAM_BOT_ACCESS_TOKEN)
