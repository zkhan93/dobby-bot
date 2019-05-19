import logging
import datetime

logfilename = '/var/log/dobby-bot/{}.log'.format(datetime.datetime.now().strftime('%Y-%m-%d'))

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO,
                    filename=logfilename
                    )
logger = logging.getLogger('dobby')
