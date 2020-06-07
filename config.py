import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'crowd_corpus_one_two_three'
    # DATABASE = os.path.join(app.instance_path, 'app.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')