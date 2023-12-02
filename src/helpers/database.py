import mysql.connector
from flask import current_app

def get_mysql_connection():
    return mysql.connector.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DB'],
        port=current_app.config['MYSQL_PORT']
    )