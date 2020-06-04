# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
from project import db

# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# # db = SQLAlchemy(app)
#
# def init_db(app):
#     return SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username