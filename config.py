import os
import pytz

# Definir la zona horaria de Ciudad de México
TIMEZONE = pytz.timezone('America/Mexico_City')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Establece la clave secreta y la clave JWT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prosmex_luis_sebas')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'prosmex_luis_sebas')
    TIMEZONE =  pytz.timezone('America/Mexico_City')

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
