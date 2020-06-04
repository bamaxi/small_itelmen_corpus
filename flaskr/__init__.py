import os

from flask import Flask, g, render_template, request
from config import Config
from markupsafe import escape

# база данных
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='corpus',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    # )
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
    # from . import database
    # db = database.init_db(app)
    db.init_app(app)


    secret_key = app.config['SECRET_KEY']

    @app.route('/')
    def index():
        # return 'Hello, World!'
        return render_template('index.html', secret_key=secret_key)

    return app


from app import models

# def main():
#     app.run(debug=True)
#
# if __name__ == '__main__':
#     main()