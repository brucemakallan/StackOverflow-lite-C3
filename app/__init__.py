from flask import Flask

from app.config import app_config
from app.database import Database


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    database_obj = Database(database='stackoverflow', host='localhost', user='postgres', password='postgres')
    return app, database_obj
