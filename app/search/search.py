from . import bp
from flask import current_app, render_template, redirect,\
    url_for, flash, g
from app import db
from app.models import User

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    word = StringField('word')
    gloss = StringField('gloss')
    submit = SubmitField('search')


@bp.route('/search', methods=['GET', 'POST'])
def search():
    # print(current_app.config)
    # print(g)
    # u = User(username='masha', email='masha@masha.com')
    # db.session.add(u)
    # db.session.commit()
    form = SearchForm()
    if form.validate_on_submit():
        # flash()
        return redirect(url_for('search_results'))

    return render_template('search/search.html', form=form)

@bp.route('/search/search_results', methods=['GET'])
def search_results():
    return render_template('search/results.html')