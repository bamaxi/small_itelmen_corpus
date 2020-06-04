# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
from datetime import datetime


from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
from app import db

# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# # db = SQLAlchemy(app)
#
# def init_db(app):
#     return SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

# class Post(db.Model):
#     __tablename__ = 'post'
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.Integer, index=True, default=0)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#     def __repr__(self):
#         return '<Post {}>'.format(self.body)

class Text(db.Model):
    __tablename__ = 'texts'
    text_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), default='')
    author = db.Column(db.String(100), default='Автор неизвестен')
    # date = db.Column()
    def __repr__(self):
        return '<Text {} (author={}, text_id={})>'.format(
            title, author, text_id)


class Paragraph(db.Model):
    __tablename__ = 'paragraphs'
    paragraph_id = db.Column(db.Integer, primary_key=True)
    text_id = db.Column(db.Integer, db.ForeignKey('texts.text_id'),
                        nullable=False)
    # order - каким-то образом порядок?
    # span - left + right с id?
    def __repr__(self):
        return '<Paragraph {} (text_id={})>'.format(
            paragraph_id, text_id)


class Phrase(db.Model):
    __tablename__ = 'phrases'
    phrase_id = db.Column(db.Integer, primary_key=True)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraphs.paragraph_id'),
                        nullable=False)
    # order - каким-то образом порядок?
    # span - left + right с id?
    def __repr__(self):
        return '<Phrase {} (paragraph_id={})>'.format(
            phrase_id, paragraph_id)

class Word(db.Model):
    __tablename__ = 'words'
    word_id = db.Column(db.Integer, primary_key=True)
    phrase_id = db.Column(db.Integer, db.ForeignKey('phrases.phrase_id'),
                             nullable=False)

    # order - каким-то образом порядок? А нужно ли именно здесь?
    text = db.Column(db.String(60), nullable=False)
    gloss = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return '<Word {} (gloss={}, phrase_id={}, word_id={})>'.format(
            text, gloss, phrase_id, word_id)

