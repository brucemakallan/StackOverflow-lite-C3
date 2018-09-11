from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import app_config


def create_app(config_name):
    """Create app using configuration name from environment variable: APP_SETTINGS"""
    app = Flask(__name__)
    CORS(app)  # for Cross Origin Requests
    app.config.from_object(app_config[config_name])
    JWTManager(app)
    return app
