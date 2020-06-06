from . import bp
from flask import redirect, url_for, render_template, request, flash
from app.update_db.update import add_data

import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField, validators
from werkzeug.utils import secure_filename

UPLOAD_DIR = 'app/upload_data/'
ALLOWED_EXTENSIONS = {'xml'}


class UploadForm(FlaskForm):
    text = FileField('файл', validators=[FileRequired()])
    submit = SubmitField('Загрузить')


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        num_files = len(os.listdir(UPLOAD_DIR))
        f = form.text.data
        filename = str(num_files+1) + '_' + secure_filename(f.filename)
        if not filename[-3:] in ALLOWED_EXTENSIONS:
            flash('Please upload a valid .xml file')
            return redirect(request.url)

        path = os.path.join(UPLOAD_DIR, filename)
        f.save(path)

        add_data(path)

        print(f'file {path} was succesfully uploaded')
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