import os
from flask import current_app


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 13
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0
    UPLOAD_FOLDER = os.path.join(
        current_app.root_path, 'uploads'
    )
    PICTURE_ALLOWED_EXTENSIONS = {'jpg', 'png', 'gif'}


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        'mysql+mysqldb://mpwo:mpwo@127.0.0.1:3306/mpwo'
    SECRET_KEY = 'development key'
    USERNAME = 'admin'
    PASSWORD = 'default'
    BCRYPT_LOG_ROUNDS = 4


class TestingConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        'mysql+mysqldb://mpwo:mpwo@127.0.0.1:3306/mpwo_test'
    SECRET_KEY = 'test key'
    USERNAME = 'admin'
    PASSWORD = 'default'
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 3
