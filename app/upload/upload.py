from . import bp
from flask import redirect, url_for, render_template, request
from app.update_db.update import add_data

import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import validators
from werkzeug.utils import secure_filename

UPLOAD_DIR = 'app/upload_data/'
# ALLOWED_EXTENSIONS = {'txt', 'xml'}


class UploadForm(FlaskForm):
    text = FileField('файл', validators=[FileRequired(),
        validators.regexp(r'^[^/\\]\.xml')])


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        num_files = len(os.listdir(UPLOAD_DIR))
        f = form.text.data
        filename = str(num_files+1) + secure_filename(f.filename)
        f.save(os.path.join(UPLOAD_DIR, filename))

        return redirect(url_for('index'))

    example_xml_path = 'app/static/example.xml'
    with open(example_xml_path, 'r', encoding='utf-8') as f:
        example_xml = f.read()

    # было:
    # { % highlight 'XmlLexer' %}
    # {{example_xml}}
    # { % endhighlight %}

    return render_template('upload/upload.html',
            form=form, example_xml=example_xml)