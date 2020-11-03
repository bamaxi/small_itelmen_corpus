import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'crowd_corpus_one_two_three'
    # DATABASE = os.path.join(app.instance_path, 'app.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_ECHO = False
    LOGGING_FILE = os.environ.get('FLASK_LOGGING_FILE') or 'logs/base.log'


loggingConfig = {
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
        },
        'file': {
         'class': 'logging.handlers.RotatingFileHandler',
         'filename': Config.LOGGING_FILE,
         'encoding': 'utf-8',
         'maxBytes': 2**23,
         'backupCount': 5,
         'formatter': 'default'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi', 'file']
    }
}