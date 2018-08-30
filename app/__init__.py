from flask import Flask
from flask_jwt_extended import JWTManager

from config import app_config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app.config['JWT_SECRET_KEY'] = 'kk38e1c32de0961d5d3bfb14f8a66e006cfb1cfbf3f0c0f5'
    JWTManager(app)
    return app
