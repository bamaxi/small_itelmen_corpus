from . import bp
from flask import render_template, redirect, url_for, request
from flask.json import dumps, loads
from app import db
from app.models import Text, Word, Morph

from sqlalchemy.orm import sessionmaker, scoped_session, aliased
from sqlalchemy import text, and_

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FormField, FieldList


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

    # remap names of search terms to table columns names
    # TODO: change something, so remap isn't necessary
    map_ = {'word_form': 'text', 'rus_lexeme': 'transl',
            'pos': 'pos', 'gloss': 'gloss', 'itl_lexeme': 'itl_lexeme'}
    UNSUPPORTED_FIELDS = ['itl_lexeme', 'pos']

    # so the loop below has something to iterate over
    # TODO: refactor
    forms_ = forms_list
    if not isinstance(forms_, list):
        forms_ = [forms_]

    total_forms_in_query = len(forms_)
    word_aliases = [aliased(Word) for i in range(total_forms_in_query)]

    # a query is then built sequentially:
    #  it is updated for each field (gloss, pos, transl, etc.) of each word
    #  since this is high-level code, it may be slow

    # create base query over multiple same tables aliased differently
    q = session.query(*word_aliases)

    for i, form in enumerate(forms_):
        cur_table = word_aliases[i]

        # make sure word forms are a part of a single phrase
        #  and that they are in the correct order
        if i != 0:
            q = q.filter(cur_table.phrase_id == word_aliases[0].phrase_id,
                         cur_table.order == word_aliases[i - 1].order + 1)
        # only leave valued AND SUPPORTED fields
        form = {map_[field]: val for field, val in form.items()
                        if (val != '' and field not in UNSUPPORTED_FIELDS)}

        # do filtering for all fields of one word form
        for field, value in form.items():
            print(field, value)
            if field == 'gloss':
                value = '%' + value.lower() + '%'
                print(value)
                # getattr(cur_table, field) is equal to `cur_table.%VALUE_OF_FIELD_VARIABLE%`
                q = q.filter(getattr(cur_table, field).ilike(text(':value'))).params(value=value)
            else:
                q = q.filter(getattr(cur_table, field) == value)
        # ####
        print(q.all())

    results = q.all()
    count = len(results)
    # print('!!!results!!!', results)
    if count == 0:
        return 0, 0, None

    # save order of found forms
    texts = []
    for result in results:
        # TODO: does it work with a single form in query?
        # TODO: does this and further code highlight multiple results
        #  in a single sentence?
        if isinstance(result, tuple):
            print('!!!A TUPLE!!!', result)
            result = result[0]
        highlight = [(result.order,
                      result.order + total_forms_in_query - 1)]
        texts.append(result.get_text_by_word(highlight))

    # TODO: fix this old code piece:
    #   (that traverses up to Text table)
    for text_dict in texts:
        # проверим, что текста с таким id ещё нет в словаре текстов
        text_id = list(text_dict.keys())[0]
        if text_id not in res:
            res.update(text_dict)
        else:
            # такой текст есть
            #  в этом случае проверим, что фразы из текущего словаря
            #  ещё нет в данных res для этого текста
            phrases = res[text_id]['phrases']
            for phrase_id, words in text_dict[text_id]['phrases'].items():
                if phrase_id not in phrases:
                    phrases[phrase_id] = words
                # наконец, проверим, были ли уже найдены эти конкретные слова
                else:
                    to_highlight = words['highlight'][0]
                    already_highlighted = phrases[phrase_id]['highlight']
                    if to_highlight not in already_highlighted:
                        already_highlighted.append(to_highlight)

    docs_count = len(res)
    # TODO: в каждую фразу на один уровень с transl добавлять список с номерами нужных слов,
    #  чтобы их выделять
    print(res)
    return count, docs_count, res


class TokenForm(FlaskForm):
    word_form = StringField('Словоформа (итл)')
    gloss = StringField('Глосса')
    rus_lexeme = StringField('Лексема (рус)')
    itl_lexeme = StringField('Лексема (итл)')

    # должно быть заполнено одно из полей
    def validate(self):
        if not super().validate():
            return False
        if (not self.word_form.data and not self.gloss.data
            and not self.rus_lexeme.data and not self.itl_lexeme.data):
            msg = 'Хотя бы одно поле должно быть заполнено'
            # TODO: можно сделать ошибки для всех
            for field in (self.word_form, self.gloss, self.rus_lexeme,
                          self.itl_lexeme):
                field.errors.append(msg)
            return False
        return True


class ManySearchForms(FlaskForm):
    tokens_list = FieldList(FormField(TokenForm), min_entries=1)
    submit = SubmitField('Поиск')


@bp.route('/search', methods=['GET', 'POST'])
def search():
    form = ManySearchForms()

    # если это форма, для которой проходит валидация, то послать запрсо
    # (валидация это в т.ч. функция в классе)
    if form.validate_on_submit():
        form_input = [
            {"word_form": token_form.word_form.data,
             "rus_lexeme": token_form.rus_lexeme.data,
             "gloss": token_form.gloss.data,
             "itl_lexeme": token_form.itl_lexeme.data}
            for token_form in form.tokens_list
        ]
        print('form is', form_input)
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
