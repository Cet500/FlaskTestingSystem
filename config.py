import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Forms config
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # DB config
    SQLALCHEMY_DATABASE_URI = os.environ.get('MySQL_DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
