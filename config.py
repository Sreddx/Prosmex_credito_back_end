import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/prosmex_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    


class localConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class QAConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/prosmex_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    