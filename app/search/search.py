import logging

from flask import render_template, redirect, url_for, request
from flask.json import dumps, loads
from sqlalchemy.orm import sessionmaker, scoped_session, aliased
from sqlalchemy import bindparam
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FormField, FieldList, ValidationError

from . import bp
from app import db
from app.models import Text, Word, Morph
from app.utils import pretty_log
# from ..testing.profiling import profiled

logger = logging.getLogger()

UNSUPPORTED_FIELDS = ['itl_lexeme', 'pos']


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

    # remap names of search terms to table columns names
    # TODO: change something, so remap isn't necessary
    map_ = {'word_form': 'text', 'rus_lexeme': 'transl',
            'pos': 'pos', 'gloss': 'gloss', 'itl_lexeme': 'itl_lexeme'}

    logger.info(f"{forms_list}")
    # so the loop below has something to iterate over
    if not isinstance(forms_list, list):
        forms_list = [forms_list]
    forms_ = forms_list
    logger.info(f"{forms_}")

    total_forms_in_query = len(forms_)
    logger.info('There are %d forms: %s', total_forms_in_query, pretty_log(forms_))

    # A query is then built sequentially:
    #  it is updated for each field (gloss, pos, transl, etc.) of each word

    # create base query over multiple same tables aliased differently
    word_aliases = [aliased(Word) for i in range(total_forms_in_query)]
    # TODO: q could be changed to fetch not whole Words, but specific fields
    #   We could already check the needed columns here!
    q = db.session.query(*word_aliases)

    # dict of parameters for "gloss" field
    #   We're not applying them consecutively as it leads to strange parameter values
    #   (next gloss replaces previous ones in `parameters` tuple)
    params = {}

    for i, form in enumerate(forms_):
        cur_table = word_aliases[i]
        # make sure word forms are a part of a single phrase
        #   and that they are in the correct order
        if i != 0:
            q = q.filter(cur_table.phrase_id == word_aliases[0].phrase_id,
                         cur_table.order == word_aliases[i - 1].order + 1)
        # only leave valued AND SUPPORTED fields
        form = {map_[field]: val for field, val in form.items()
                if (val != '' and field not in UNSUPPORTED_FIELDS)}

        # do filtering for all fields of one word form
        for field, value in form.items():
            if field == 'gloss':
                value = '%' + value.lower() + '%'
                # getattr(cur_table, field) is equal to `cur_table.%VALUE_OF_FIELD_VARIABLE%`
                params[f'gloss{i}'] = value  # or text(value)
                q = q.filter(getattr(cur_table, field).ilike(bindparam(f'gloss{i}')))
            else:
                q = q.filter(getattr(cur_table, field) == value)
                logger.debug('in after field, val is `%s`', value)

    results = q.params(**params).all()
    count = len(results)
    logger.info("The result is %d long", count)

    if count == 0:
        return 0, 0, None

    # save order of found forms
    texts = []
    for result in results:
        # TODO: This code and templates/search/results.html
        #   creates new boxes for results occuring in same sentence
        #   is it desirable?
        if isinstance(result, tuple):
            result = result[0]
        highlight = [(result.order,
                      result.order + total_forms_in_query - 1)]
        texts.append(result.get_text_by_word(highlight))

    for candidate_text_dict in texts:
        # проверим, что текста с таким id ещё нет в словаре текстов
        candidate_text_id = list(candidate_text_dict.keys())[0]
        if candidate_text_id not in res:
            res.update(candidate_text_dict)
        else:
            # такой текст есть
            #  в этом случае проверим, что фразы из текущего словаря
            #  ещё нет в данных res для этого текста
            phrases = res[candidate_text_id]['phrases']
            for candidate_phrase_id, candidate_words in \
                    candidate_text_dict[candidate_text_id]['phrases'].items():
                if candidate_phrase_id not in phrases:
                    phrases[candidate_phrase_id] = candidate_words
                # наконец, проверим, были ли уже найдены эти конкретные слова
                else:
                    candidate_to_highlight = candidate_words['highlight'][0]
                    already_highlighted = phrases[candidate_phrase_id]['highlight']
                    if candidate_to_highlight not in already_highlighted:
                        already_highlighted.append(candidate_to_highlight)

    docs_count = len(res)
    logger.debug('Results are:\n%s', pretty_log(res))
    return count, docs_count, res


class TokenForm(FlaskForm):
    word_form = StringField('Словоформа (итл)')
    gloss = StringField('Глосса')
    rus_lexeme = StringField('Лексема (рус)')
    itl_lexeme = StringField('Лексема (итл)')

    # # должно быть заполнено одно из полей
    # def validate(self):
    #     if not super().validate():
    #         return False
    #     if (not self.word_form.data and not self.gloss.data and
    #             not self.rus_lexeme.data and not self.itl_lexeme.data):
    #         msg = 'Хотя бы одно поле должно быть заполнено'
    #         # TODO: можно сделать ошибки для всех
    #         for field in (self.word_form, self.gloss, self.rus_lexeme,
    #                       self.itl_lexeme):
    #             field.errors.append(msg)
    #         return False
    #     return True


def ensure_first_and_last_filled(big_form, fieldslist):
    first_form = fieldslist[0]
    last_form = fieldslist[-1]

    ff_has_values = [1 if field.data else 0 for field in first_form]
    lf_has_values = [1 if field.data else 0 for field in last_form]

    if not (any(ff_has_values) and any(lf_has_values)):
        raise ValidationError('first and last wordforms should always be specified')


class ManySearchForms(FlaskForm):
    tokens_list = FieldList(FormField(TokenForm), [ensure_first_and_last_filled],
                            min_entries=1)
    submit = SubmitField('Поиск')


@bp.route('/search', methods=['GET', 'POST'])
def search():
    form = ManySearchForms()

    # если это форма, для которой проходит валидация, то послать запрос
    #   (валидация это в т.ч. функция в классе)
    if form.validate_on_submit():
        form_input = [
            {"word_form": token_form.word_form.data,
             "rus_lexeme": token_form.rus_lexeme.data,
             "gloss": token_form.gloss.data,
             "itl_lexeme": token_form.itl_lexeme.data}
            for token_form in form.tokens_list
        ]
        # logger.info('form is', pretty_log(form_input))
        return redirect(url_for('.search_results', query=dumps(form_input)))

    total = get_total_for_corpus()
    return render_template('search/search.html', form=form, **total)


@bp.route('/search/search_results', methods=['GET'])
def search_results():
    query = request.args['query']
    query = loads(query)

    logger.info(f"query is {pretty_log(query)}")
    count, docs_count, res = do_search(query)

    total = get_total_for_corpus()
    return render_template('search/results.html',
                           count=count, docs_count=docs_count, res=res,
                           **total)
