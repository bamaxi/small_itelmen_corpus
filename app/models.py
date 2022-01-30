# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
from sqlalchemy.orm import relationship
from app import db


class Text(db.Model):
    __tablename__ = 'texts'
    # TODO: add metadata on text? Filename, date of adding..
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

    def __repr__(self):
        return '<Paragraph {} (text_id={})>'.format(
            self.paragraph_id, self.text_id)


class Phrase(db.Model):
    __tablename__ = 'phrases'
    phrase_id = db.Column(db.Integer, primary_key=True)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraphs.paragraph_id'),
                             nullable=False)
    transl = db.Column(db.String(200))

    # many-to-one предложения к абазцу
    paragraph = relationship('Paragraph', back_populates='phrases')

    # one-to-many предложения к словам
    words = relationship('Word', order_by='Word.word_id',
                         back_populates='phrase')

    def get_phrase_with_word_glosses(self, highlight):
        """
        получить для предложения словарь с разборами всех слов в нём
        и переводом
        :param highlight: list of 2-tuples with left and right border for highlight
                        (in case we need to highlight multiple parts of sentence)
        :return:
        """
        phrase = {'transl': self.transl, 'highlight': highlight}
        words = [word.get_word_with_glosses()
                 for word in self.words]
        phrase['words'] = words
        return phrase

    def __repr__(self):
        return '<Phrase {} (paragraph_id={}, words={})>'.format(
            self.phrase_id, self.paragraph_id, self.words)


# https://web.archive.org/web/20150909165001/http://www.ferdychristant.com/blog//articles/DOMM-7QJPM7
class Word(db.Model):
    """
    одно слово - форма (text), часть речи (pos), перевод (transl)
    """
    __tablename__ = 'words'
    word_id = db.Column(db.Integer, primary_key=True)
    phrase_id = db.Column(db.Integer, db.ForeignKey('phrases.phrase_id'),
                             nullable=False)
    # many-to-one предложения к абазцу
    phrase = relationship('Phrase', back_populates='words')

    text = db.Column(db.String(60), nullable=False)
    # везде было nullable=False
    gloss = db.Column(db.String(60))
    pos = db.Column(db.String(20))
    transl = db.Column(db.String(60))
    position = db.Column(db.Integer)

    # one-to-many к морфам
    morphs = relationship('Morph', order_by='Morph.morph_id', back_populates='word')

    def get_word_with_glosses(self):
        """
        получить словарь с информацией о слове и собранными воедино морфами
        :return:
        """
        full_word = {'word': self.text, 'rus_lexeme': '',
                     'itl_lexeme': '',
                     'dash': '', 'gloss': '', 'base': ''}

        for morph in self.morphs:
            # выбрать лексему (русский)
            # TODO: ещё глоссируют 'bound stem' иногда
            full_word['rus_lexeme'] = self.transl
            if morph.type == 'stem':
                full_word['itl_lexeme'] = morph.base_form
            full_word['dash'] += morph.text

            try:
                full_word['gloss'] += morph.gloss + '-'
                full_word['base'] += morph.base_form + '|'
            except TypeError:
                # something is None and we're concatenating None + str
                continue

        full_word['gloss'] = full_word['gloss'].rstrip('-')
        full_word['base'] = full_word['base'].rstrip('|')
        return full_word

    def get_text_by_word(self, highlight):
        """
        функция идущая по иерархии снизу вверх, а потом сверху вниз
        По морфу получить словарь, где верхний уровень - текст
        :return: словарь, описывающий одно слово из текста, предложение и текст
        """
        text_by_word = {}
        text = self.phrase.paragraph.text

        # два уровня вложенности, чтобы быстро проверять совпадения
        # верхний уровень - id текста, ниже словарь с информацией о тексте и вложенным
        # словарём фраз=предложений (параграфы не используются)
        text_by_word[text.text_id] = {'author': text.author, 'title': text.title,
                                      'phrases': {}}

        phrase = self.phrase
        text_by_word[text.text_id]['phrases'][phrase.phrase_id] = \
            phrase.get_phrase_with_word_glosses(highlight)

        return text_by_word

    def __repr__(self):
        return '<Word {} (gloss={}, phrase_id={}, word_id={}, position={})>'.format(
            self.text, self.gloss, self.phrase_id, self.word_id, self.position)


class Morph(db.Model):
    __tablename__ = 'morphs'
    morph_id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.word_id'),
                        nullable=False)
    # many-to-one морфы к слову
    word = relationship('Word', back_populates='morphs')

    # везде было nullable=False
    text = db.Column(db.String(60), nullable=False)
    base_form = db.Column(db.String(60))
    type = db.Column(db.String(60))
    gloss = db.Column(db.String(60))
    pos = db.Column(db.String(20))

    # функция идущая по иерархии снизу вверх, а потом сверху вниз
    # По морфу получить словарь, где верхний уровень - текст
    def get_text_by_morph(self):
        text_by_morph = self.word.get_text_by_word()
        return text_by_morph

    def __repr__(self):
        return '<Morph {} (gloss={}, base_form={}, type={}, pos={}, word_id={})>'.format(
            self.text, self.gloss, self.base_form, self.type, self.pos, self.word_id)


# class Author(db.Model):
#     __tablename__ = 'authors'
#     author_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#
#     # one-to-many автор к текстам
#     texts = relationship('Text', order_by=Text.text_id,
#                          back_populates='author')
#
#     def __repr__(self):
#         return '<Author {} (author_id={})>'.format(
#             self.name, self.author_id)