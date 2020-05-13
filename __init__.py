import os, sqlite3


from flask import Flask, g, render_template, request
from markupsafe import escape

# DATABAS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='corpus',
        DATABASE=os.path.join(app.instance_path, 'Project.sqlite')
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        # return 'Hello, World!'
        return render_template('index.html')
    return app

# def main():
#     app.run(debug=True)
#
# if __name__ == '__main__':
#     main()