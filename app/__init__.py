import os
from pathlib import Path
import logging
from logging.config import dictConfig

from werkzeug.debug import DebuggedApplication
from flask import Flask, render_template

# база данных
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

from config import Config, loggingConfig

# create logging dir if needed
path = Path(Config.LOGGING_FILE)
try:
    os.makedirs(path.parent)
except OSError:
    pass

dictConfig(loggingConfig)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile('config.py', silent=True)
        # or from CLass (needs to be imported from module)
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # инициализация базы данных
    db.init_app(app)
    migrate.init_app(app, db)

    # инициализация бутстрапа
    Bootstrap(app)

    # blueprint для поиска
    from app.search import bp as search_bp
    app.register_blueprint(search_bp)

    # blueprint для обновления базы данных
    from app.update_db import bp as update_db_bp
    app.register_blueprint(update_db_bp)

    # blueprint для загрузки файла
    from app.upload import bp as upload_bp
    app.register_blueprint(upload_bp)

    # blueprint для ошибок
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # blueprint для главной страницы
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    return app


from app import models
