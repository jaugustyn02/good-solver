import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'r6\xb5\xd9K\xd5\t\x84X}\x16\x88\xf0t^\x15\xaf\xadn)\xca\xf7\xd4k'
    MYSQL_HOST = os.environ.get('HOST')
    MYSQL_USER = os.environ.get('USER_NAME')
    MYSQL_PASSWORD = os.environ.get('PASSWORD')
    MYSQL_DB = os.environ.get('DB')
    MYSQL_PORT = os.environ.get('PORT')


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass


if os.environ.get('FLASK_ENV') == 'development':
    app_config = DevelopmentConfig
else:
    app_config = ProductionConfig
