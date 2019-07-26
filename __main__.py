from dotenv import Dotenv
import os

if __name__ == '__main__':
        
    base_dir = os.path.dirname(os.path.realpath(__file__))
    environment_variables = Dotenv(os.path.join(base_dir, ".env"))
    os.environ.update(environment_variables)

    from dobby_bot import TelegramBot
    TelegramBot(base_dir).start()
