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
        if not os.path.exists(UPLOAD_DIR):
            print(f'creating path at {UPLOAD_DIR}')
            os.mkdir(UPLOAD_DIR)

        num_files = len(os.listdir(UPLOAD_DIR))
        f = form.text.data
        filename = str(num_files+1) + '_' + secure_filename(f.filename)
        if not filename[-3:] in ALLOWED_EXTENSIONS:
            flash('Please upload a valid .xml file')
            return redirect(request.url)

        path = os.path.join(UPLOAD_DIR, filename)

        f.save(path)
        print(f'file {path} was successfully uploaded')

        count_unique, count_total, unique_texts_in_file = add_data(path)
        print(f'file {path} was parsed. '
              f'Unique (new) texts {count_unique}, total texts {count_total} '
              f'unique texts are {unique_texts_in_file}')

        message = f'We were able to parse {count_total} texts.\n'
        if count_unique == 0:
            message += f'Unfortunately, all texts with these titles were already in the corpus.'
        else:
            message += f'Of these {count_unique} were not present in the corpus. Thank you!'

        flash('Thank you! Your file was successfully uploaded.\n' + message)
        return redirect(url_for('main.index'))

    example_xml_path = 'app/static/example.xml'
    with open(example_xml_path, 'r', encoding='utf-8') as f:
        example_xml = f.read()

    # было в шаблоне:
    # { % highlight 'XmlLexer' %}
    # {{example_xml}}
    # { % endhighlight %}

    return render_template('upload/upload.html',
            form=form, example_xml=example_xml)