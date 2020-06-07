import os

from flask import Flask, render_template
from config import Config
from werkzeug.debug import DebuggedApplication

# import jinja2_highlight
# import pygments
# from pygments import lexers

# база данных
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

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

    # jinja_options = dict(Flask.jinja_options)
    # jinja_options.setdefault('extensions',
    #                          []).append('jinja2_highlight.HighlightExtension')
    # app.jinja_env.extend(jinja2_highlight_cssclass='codehilite')
    # app.jinja_env.add_extension("jinja2_highlight.HighlightExtension")

    secret_key = app.config['SECRET_KEY']

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    # @app.route('/')
    # def index():
    #     # return 'Hello, World!'
    #     return render_template('index.html')
    return app


from app import models
