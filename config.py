import os
import pytz
from datetime import timedelta

# Definir la zona horaria de Ciudad de México
TIMEZONE = pytz.timezone('America/Mexico_City')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Establece la clave secreta y la clave JWT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prosmex_luis_sebas')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'prosmex_luis_sebas')
    # Convert the environment variables to integers and create timedelta objects
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 15))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30))
    )
    # Split the JWT_TOKEN_LOCATION environment variable into a list
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', False)
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = True
    FLASK_APP = os.environ.get('FLASK_APP', 'app.py')

class localConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    # Puedes sobrescribir las claves si es necesario en el entorno local
    SECRET_KEY = os.environ.get('LOCAL_SECRET_KEY', Config.SECRET_KEY)
    JWT_SECRET_KEY = os.environ.get('LOCAL_JWT_SECRET_KEY', Config.JWT_SECRET_KEY)


class QAConfig(Config):
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Puedes sobrescribir las claves si es necesario en el entorno de QA
    SECRET_KEY = os.environ.get('QA_SECRET_KEY', Config.SECRET_KEY)
    JWT_SECRET_KEY = os.environ.get('QA_JWT_SECRET_KEY', Config.JWT_SECRET_KEY)
