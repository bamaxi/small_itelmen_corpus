# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
from datetime import datetime


from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from app import db

# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# # db = SQLAlchemy(app)
#
# def init_db(app):
#     return SQLAlchemy(app)




class Text(db.Model):
    __tablename__ = 'texts'
    text_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), default='Неизвестный текст')
    author = db.Column(db.String(100), default='Автор неизвестен')
    # author_id = db.Column(db.Integer, db.ForeignKey('Author.author_id'),
    #                       nullable=False)

    # many-to-one тексты к автору
    # author_obj = relationship('Author', back_populates='texts')



    # date = db.Column()
    # one-to-many: текст ко многим абзацам
    paragraphs = relationship('Paragraph', order_by='Paragraph.paragraph_id',
                              back_populates='text')

    def __repr__(self):
        return '<Text {} (author={}, text_id={})>'.format(
            self.title, self.author, self.text_id)


class Paragraph(db.Model):
    __tablename__ = 'paragraphs'
    paragraph_id = db.Column(db.Integer, primary_key=True)
    text_id = db.Column(db.Integer, db.ForeignKey('texts.text_id'),
                        nullable=False)
    # many-to-one абзацы к тексту, back_populates как one-to-many Текста
    text = relationship('Text', back_populates='paragraphs')

    # one-to-many Абзац к предложениям
    phrases = relationship('Phrase', order_by='Phrase.phrase_id',
                           back_populates='paragraph')

    # order - каким-то образом порядок?
    # span - left + right с id?
    def __repr__(self):
        return '<Paragraph {} (text_id={})>'.format(
            self.paragraph_id, self.text_id)


class Phrase(db.Model):
    __tablename__ = 'phrases'
    phrase_id = db.Column(db.Integer, primary_key=True)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraphs.paragraph_id'),
                        nullable=False)

    # many-to-one предложения к абазцу
    paragraph = relationship('Paragraph', back_populates='phrases')

    # one-to-many предложения к словам
    words = relationship('Word', order_by='Word.phrase_id',
                         back_populates='phrase')

    # order - каким-то образом порядок?
    # span - left + right с id?
    def __repr__(self):
        return '<Phrase {} (paragraph_id={})>'.format(
            self.phrase_id, self.paragraph_id)



#https://web.archive.org/web/20150909165001/http://www.ferdychristant.com/blog//articles/DOMM-7QJPM7
# TODO: add parent - previous word and desc - next word
# TODO: add lineage - word order (for each?) or for sentences actually?
class Word(db.Model):
    '''
    одно слово - форма (text), часть речи (pos), перевод (transl)

    '''
    __tablename__ = 'words'
    word_id = db.Column(db.Integer, primary_key=True)
    phrase_id = db.Column(db.Integer, db.ForeignKey('phrases.phrase_id'),
                             nullable=False)
    # many-to-one предложения к абазцу
    phrase = relationship('Phrase', back_populates='words')

    # order - каким-то образом порядок? А нужно ли именно здесь?
    text = db.Column(db.String(60), nullable=False)
    # везде было nullable=False
    gloss = db.Column(db.String(60))
    pos = db.Column(db.String(20))
    transl = db.Column(db.String(60))

    # one-to-many к морфам
    morphs = relationship('Morph', order_by='Morph.morph_id', back_populates='word')

    # def get_word_with_glosses(self):

    def __repr__(self):
        return '<Word {} (gloss={}, phrase_id={}, word_id={})>'.format(
            self.text, self.gloss, self.phrase_id, self.word_id)


class Morph(db.Model):
    '''
    морфы
    type - префикс/основа/суффикс
    '''
    __tablename__ = 'morphs'
    morph_id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.word_id'),
                          nullable=False)
    # many-to-one морфы к слову
    word = relationship('Word', back_populates='morphs')

    ### везде было nullable=False
    text = db.Column(db.String(60), nullable=False)
    base_form = db.Column(db.String(60))
    type = db.Column(db.String(60))
    gloss = db.Column(db.String(60))
    pos = db.Column(db.String(20))
    # order - каким-то образом порядок? А нужно ли именно здесь?

    def __repr__(self):
        return '<Morph {} (gloss={}, base_form={}, type={}, pos={}, word_id={})>'.format(
            self.text, self.gloss, self.base_form, self.type, self.pos, self.word_id)




# class Author(db.Model):
#     __tablename__ = 'authors'
#     author_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#
#     # one-to-many автор к текстам
#     texts = relationship('Text', #order_by=Text.text_id,
#                          back_populates='author')
#
#     def __repr__(self):
#         return '<Author {} (author_id={})>'.format(
#             self.name, self.author_id)
#


class User(db.Model):
    __tablename__ = 'users'
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