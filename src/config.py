import os

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'r6\xb5\xd9K\xd5\t\x84X}\x16\x88\xf0t^\x15\xaf\xadn)\xca\xf7\xd4k'
    MYSQL_HOST = 'mysql.agh.edu.pl'
    MYSQL_USER = 'jaugusty'
    MYSQL_PASSWORD = 'jbJPBNJmrWipaigs'
    MYSQL_DB = 'jaugusty'
    MYSQL_PORT = 3306

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass


if os.environ.get('FLASK_ENV') == 'development':
    app_config = DevelopmentConfig
else:
    app_config = ProductionConfig
