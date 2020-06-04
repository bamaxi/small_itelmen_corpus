import os

class Config(object):
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECRET_KEY = 'crowd_corpus'
    # DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'