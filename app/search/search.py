from . import bp
from flask import current_app, render_template, redirect,\
    url_for, flash, g
from app import db
from app.models import User, Word

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    word = StringField('word')
    gloss = StringField('gloss')
    submit = SubmitField('search')


# url_for('search.search') - снаружи
# или '.search' - внутри чертежа
@bp.route('/search', methods=['GET', 'POST'])
def search():
    # print(g)
    # u = User(username='alyona', email='alyona@masha.com')
    # db.session.add(u)
    # db.session.commit()
    word = Word(phrase_id=1, text='рамы', gloss='мыть-3PL')
    db.session.add(word)
    db.session.commit()

    print(User.query.all())
    raise
    form = SearchForm()
    if form.validate_on_submit():
        # flash()
        return redirect(url_for('search_results'))

    return render_template('search/search.html', form=form)

@bp.route('/search/search_results', methods=['GET'])
def search_results():
    # TODO: пример запроса на глоссу:
    # q_3pl = db.session.query(Word).filter(Word.gloss.ilike(text(':_gloss'))).params(_gloss='%'+"3pl"+'%')


    return render_template('search/results.html')