"""
This file initializes the application and all external components
connected to the application
"""
from flask import Flask
from config import config
from flask_mongoengine import MongoEngine
import tensorflow as tf
from flask_caching import Cache
from flask_cors import CORS
from flask_mail import Mail

forecast_model = tf.keras.models.load_model('app/forecast_model/aqi-model-v1.h5') #ML Model
db = MongoEngine() #MongoDB Data Base 
cache = Cache() #Caching
cors = CORS() #Cross Origin Requests
mail = Mail() #Email


def create_app(config_name):
    #initializes the application based on the given configuration
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    mail.init_app(app)

    #registers the api (v1) blueprint
    from .resource import api_bp as api_blueprint


    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
