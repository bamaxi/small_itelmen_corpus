from flask import render_template

from . import bp
from app import db
from app.models import Text, Word, Morph



@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    q = db.session.query(Text.title, Text.source)

    texts = q.all()
    print(texts)

    return render_template('main/index.html', texts=texts)