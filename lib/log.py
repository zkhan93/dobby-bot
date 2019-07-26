import logging
import logging.config
import sys

logfilename = '/var/log/dobby-bot/app.log'

logging.config.dictConfig({
    'version': 1,
    'root': {
        'level': logging.INFO,
        'handlers': ['console', 'file']
    },
    'formatters': {
        'default_formatter': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': logging.INFO,
            'formatter': 'default_formatter',
            'stream': sys.stdout
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': logging.INFO,
            'formatter': 'default_formatter',
            'filename': logfilename,
            'maxBytes': 512,
            'backupCount': 3
        }
    }
})

logger = logging.getLogger('root')