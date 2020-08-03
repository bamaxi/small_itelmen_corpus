from . import bp
from flask import current_app, render_template, redirect, \
    url_for, request
from flask.json import dumps, loads
from app import db
from app.models import Text, Word, Morph

from sqlalchemy.orm import sessionmaker, scoped_session, aliased
from sqlalchemy import text, and_

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


def get_total_for_corpus():
    """
    узнать текущее число текстов и словоформ в корпусе
    """
    return {'total_words': Word.query.count(),
            'total_docs': Text.query.count()}


def do_search(forms_list):
    """

    :param forms_list:
    :return: number of sentences, number of documents,
        dictionary describing document and containing sentences
    """
    res = {}

    session = db.session

    map_ = {'word_form': 'text', 'rus_lexeme': 'transl',
            'pos': 'pos', 'gloss': 'gloss'}

    forms_ = forms_list
    if not isinstance(forms_, list):
        forms_ = [forms_]
    total_forms_in_query = len(forms_)
    word_aliases = [aliased(Word) for i in range(total_forms_in_query)]

    q = session.query(*word_aliases)

    for i, form in enumerate(forms_):
        cur_table = word_aliases[i]

        # make sure word forms are a part of a single phrase
        #  and that they are in the correct order
        if i != 0:
            q = q.filter(cur_table.phrase_id == word_aliases[0].phrase_id,
                         cur_table.order == word_aliases[i - 1].order + 1)
        # only leave valued fields
        form = {map_[field]: val for field, val in form.items() if val != ''}

        # do filtering for all fields of one word form
        for field, value in form.items():
            print(field, value)
            if field == 'gloss':
                value = '%' + value.lower() + '%'
                print(value)
                q = q.filter(getattr(cur_table, field).ilike(text(':value'))).params(value=value)
            else:
                q = q.filter(getattr(cur_table, field) == value)

        results = q.all()
        count = len(results)
        if count == 0:
            return
        # save order of found forms
        texts = []
        for result in results:
            # TODO: does it work with a single form in query?
            if isinstance(result, tuple):
                result = result[0]
            highlight = [(result.order,
                          result.order + total_forms_in_query - 1)]
            texts.append(result.get_text_by_word(highlight))

        # TODO: fix this old code piece:
        for text_dict in texts:
            # проверим, что текста с таким id ещё нет в словаре текстов
            text_id = list(text_dict.keys())[0]
            if text_id not in res:
                res.update(text_dict)

            # такой текст есть
            # в этом случае проверим, что фразы из текущего словаря
            # ещё нет в данных res для этого текста
            phrases = res[text_id]['phrases']
            for phrase_id, words in text_dict[text_id]['phrases'].items():
                if phrase_id not in phrases:
                    phrases[phrase_id] = words

        docs_count = len(res)
        # TODO: в каждую фразу на один уровень с transl добавлять список с номерами нужных слов,
        # TODO: чтобы их выделять
        print(res)
        return count, docs_count, res


# def do_search(include_base_form=True, **search_params):
#     """
#     :param include_base_form: находить ли глубинные формы алломорфов
#     :param search_params: some or all of:
#         word_form - словоформа, колонка Word.text,
#         gloss - глосса, колонка Morph.gloss,
#         rus_lexeme - лексема на русском, колонка Word.transl,
#         itl_lexeme - лексема на ительменском, Morph.base_form для type=stem
#     :return: count, dict of texts
#     """
#     count = 0
#     res = {}
#
#     word_form = search_params.get('word_form', '')
#     rus_lexeme = search_params.get('rus_lexeme', '')
#     gloss = search_params.get('gloss', '')
#     itl_lexeme = search_params.get('itl_lexeme', '')
#
#     # можно делать join, тогда возвращать только Word
#     # или query(Word, Morph) тогда возвращать список кортежей
#     # при втором можно добиться выделения хорошего
#     joined = db.session.query(Word).join(Morph)
#     print(joined.filter(Word.transl == rus_lexeme).all())
#     # фильтры по Word
#     if word_form != '':
#         joined = joined.filter(Word.text == word_form)
#     if rus_lexeme != '':
#         joined = joined.filter(Word.transl == rus_lexeme)
#     # фильтры по Morph
#     # TODO: искать через LIKE не идеально, могут браться не полные глоссы,
#     # TODO: ... а части других глосс тоже (?)
#     if gloss != '':
#         gloss = '%' + gloss.lower() + '%'
#         joined = joined.filter(
#             Morph.gloss.ilike(text(':gloss'))).params(
#                 gloss=gloss)
#
#     if itl_lexeme != '':
#         joined = joined.filter(and_(Morph.type=='stem',
#                                     Morph.base_form == itl_lexeme))
#
#     # для каждой формы получить словарь вплоть до текста
#     # объединить дублирующиеся словари
#     # TODO: всё это неэкономно, поправить
#     # TODO: кажется, здесь достаточно if count == 0 и не надо ловить исключение
#     joined_all = joined.all()
#     count = len(joined_all)
#     try:
#         texts_for_words = [word.get_text_by_word(
#                 include_base_form=include_base_form
#             ) for word in joined_all]
#
#         res = texts_for_words[0]
#     except IndexError:
#         return 0, 0, {}
#
#     for text_dict in texts_for_words:
#         # проверим, что текста с таким id ещё нет в словаре текстов
#         text_id = list(text_dict.keys())[0]
#         if text_id not in res:
#             res.update(text_dict)
#
#         # такой текст есть
#         # в этом случае проверим, что фразы из текущего словаря
#         # ещё нет в данных res для этого текста
#         phrases = res[text_id]['phrases']
#         for phrase_id, words in text_dict[text_id]['phrases'].items():
#             if phrase_id not in phrases:
#                 phrases[phrase_id] = words
#
#     docs_count = len(res)
#     # TODO: в каждую фразу на один уровень с transl добавлять список с номерами нужных слов,
#     # TODO: чтобы их выделять
#     print(res)
#     return count, docs_count, res


class SearchForm(FlaskForm):
    word_form = StringField('Словоформа (итл)')
    gloss = StringField('Глосса')
    rus_lexeme = StringField('Лексема (рус)')
    itl_lexeme = StringField('Лексема (итл)')
    submit = SubmitField('Поиск')

    # должно быть заполнено одно из полей
    def validate(self):
        if not super(SearchForm, self).validate():
            return False
        if (not self.word_form.data and not self.gloss.data
            and not self.rus_lexeme.data and not self.itl_lexeme.data):
            msg = 'Хотя бы одно поле должно быть заполнено'
            # TODO: можно сделать ошибки для всех
            for field in (self.word_form, self.gloss, self.rus_lexeme, self.itl_lexeme):
                field.errors.append(msg)
            return False
        return True


@bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()

    # если это форма, для которой проходит валидация, то послать запрсо
    # (валидация это в т.ч. функция в классе)
    if form.validate_on_submit():
        form_input = [{"word_form": form.word_form.data,
            "rus_lexeme": form.rus_lexeme.data, "gloss": form.gloss.data,
            "itl_lexeme": form.itl_lexeme.data}]
        return redirect(url_for('.search_results', query=dumps(form_input)))

    total = get_total_for_corpus()
    return render_template('search/search.html', form=form, **total)


@bp.route('/search/search_results', methods=['GET'])
def search_results():
    query = request.args['query']
    query = loads(query)
    print(type(query), 'query:', query)

    # new session
    # TODO: this may be bad practice and in need of fixing
    # engine = db.session.get_bind()
    # session_factory = sessionmaker(bind=engine)
    # Session = scoped_session(session_factory)
    print(query)
    count, docs_count, res = do_search(query)

    total = get_total_for_corpus()
    return render_template('search/results.html',
                           count=count, docs_count=docs_count, res=res,
                           **total)
