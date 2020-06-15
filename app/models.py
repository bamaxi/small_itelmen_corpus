# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
from sqlalchemy.orm import relationship
from app import db


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

    def get_phrase_with_word_glosses(self, include_base_form=False):
        """
        получить для предложения словарь с разборами всех слов в нём
        и переводом
        :param include_base_form:
        :return:
        """
        phrase = {'transl': self.transl}
        words = [word.get_word_with_glosses(
                    include_base_form=include_base_form)
                 for word in self.words]
        phrase['words'] = words
        return phrase

    def __repr__(self):
        return '<Phrase {} (paragraph_id={})>'.format(
            self.phrase_id, self.paragraph_id)

#https://web.archive.org/web/20150909165001/http://www.ferdychristant.com/blog//articles/DOMM-7QJPM7
# TODO?: add parent - previous word and desc - next word
# TODO?: add lineage - word order (for each?) or for sentences actually?
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

    text = db.Column(db.String(60), nullable=False)
    # везде было nullable=False
    gloss = db.Column(db.String(60))
    pos = db.Column(db.String(20))
    transl = db.Column(db.String(60))

    # one-to-many к морфам
    morphs = relationship('Morph', order_by='Morph.morph_id', back_populates='word')

    def get_word_with_glosses(self, include_base_form=False):
        """
        получить словарь с информацией о слове и собранными воедино морфами
        :param include_base_form:
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
            # TODO: добавить глоссу через дефис к колонкам Word, чтобы лучше искать глоссы
            # хотя все равно не спасает..
            try:
                full_word['gloss'] += morph.gloss + '-'
                if include_base_form==True:
                    full_word['base'] += morph.base_form + '|'
            except TypeError:
                # something is None and we're concatenating None + str
                continue

        full_word['gloss'] = full_word['gloss'].rstrip('-')
        full_word['base'] = full_word['base'].rstrip('|')
        return full_word

    def get_text_by_word(self, include_base_form=False):
        # TODO: в таком словаре как раз основное неудобство
        """
        функция идущая по иерархии снизу вверх, а потом сверху вниз
        По морфу получить словарь, где верхний уровень - текст
        :param include_base_form:
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
        # похожим образом здесь ключ phrase_id, дальше их список
        phrases_list = []
        text_by_word[text.text_id]['phrases'][phrase.phrase_id] = phrases_list
        phrases_list.append(phrase.get_phrase_with_word_glosses(
            include_base_form=include_base_form))

        return text_by_word

    def __repr__(self):
        return '<Word {} (gloss={}, phrase_id={}, word_id={})>'.format(
            self.text, self.gloss, self.phrase_id, self.word_id)


class Morph(db.Model):
    # type - префикс/основа/суффикс
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