"""
This file contains all configurations/environment variables for the application.
Namely -- testing config, development config (default), production config
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))
import certifi
ca = certifi.where()


class Config:
    """
    The Config class is the parent class to the application configurations.
    This class contains all environment variables for the application.
    """
    ca = certifi.where()
    SECRET_KEY = os.environ.get('SECRET_KEY')

    CACHE_TYPE = 'simple'
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = False
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 

    MAIL_SUBJECT_PREFIX = '[OpenAQI]'
    MAIL_SENDER = 'OpenAQI Support <support@openaqi.io>'
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    The DevelopmentConfig class is the application configuration during development
    """
    DEBUG = True
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    MONGODB_SETTINGS = os.environ.get('MONGODB_SETTINGS') or {
        'db': 'openaqi',
        'host': f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.d1nde.mongodb.net/openaqi",
        'username': MONGO_USERNAME,
        'password': MONGO_PASSWORD,
        'TLSCAFile': ca
    }


class TestingConfig(Config):
    """
    The TestingConfig class is the application configuration during testing
    """
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    

class ProductionConfig(Config):
    """
    The ProductionConfig class is the application configuration during production
    """
    TESTING = False
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    MONGODB_SETTINGS = os.environ.get('MONGODB_SETTINGS') or {
        'db': 'openaqi',
        'host': f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.d1nde.mongodb.net/openaqi",
        'username': MONGO_USERNAME,
        'password': MONGO_PASSWORD,
        'TLSCAFile': ca
    }

#dict of configurations refenced when app is initialized
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    
    'default': DevelopmentConfig
}