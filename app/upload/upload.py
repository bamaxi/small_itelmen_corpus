import logging
import os

from flask import redirect, url_for, render_template, request, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField
from werkzeug.utils import secure_filename
from markupsafe import Markup

from . import bp
from app.update_db.update import add_data

UPLOAD_DIR = 'app/upload_data/'
ALLOWED_EXTENSIONS = {'xml'}

logger = logging.getLogger()


class UploadForm(FlaskForm):
    text = FileField('Выберите файл:', validators=[FileRequired()])
    submit = SubmitField('Загрузить')


# TODO: сейчас после загрузки пользователь должен ждать, пока файл распарсится и добавится в таблицу.
# TODO: ...это надо делать асинхронно, например, через *Celery* и потом узнавать Фласком успешность парсинга
@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()

    # если это запрос POST с валидированной формой, то...
    # (валидаторы - в т.ч. из класса `UploadForm` - требование файла)
    if form.validate_on_submit():
        if not os.path.exists(UPLOAD_DIR):
            logger.debug(f'creating path at {UPLOAD_DIR}')
            os.mkdir(UPLOAD_DIR)

        # сохранить файл в виде N_название-файла-пользователя
        # но очищенное от html кода через `secure_filename`
        num_files = len(os.listdir(UPLOAD_DIR))
        f = form.text.data
        filename = str(num_files+1) + '_' + secure_filename(f.filename)
        if not filename[-3:] in ALLOWED_EXTENSIONS:
            flash('Пожалуйста, загрузите .xml файл указанного вида', 'warning')
            return redirect(request.url)

        path = os.path.join(UPLOAD_DIR, filename)

        f.save(path)
        logger.debug(f'file {path} was successfully uploaded')

        count_unique, count_total, unique_texts_in_file = add_data(path)
        logger.info(
              f'file {path} was parsed. '
              f'Unique (new) texts {count_unique}, total texts {count_total} '
              f'unique texts are {unique_texts_in_file}')

        message = f' Спасибо! Ваш файл успешно загружен. '\
                  f'Нам удалось обработать {count_total} текстов.\n'
        if count_unique == 0:
            message += f'К сожалению, все тексты с такими заголовками уже представлены в корпусе.'
        else:
            message += f'Из них {count_unique} с такими заголовками не было в корпусе. Спасибо!'

        message = Markup(message.replace('\n', '<br />'))
        flash(message)

        return redirect(url_for('main.index'))

    example_xml_path = 'app/static/example.xml'
    with open(example_xml_path, 'r', encoding='utf-8') as f:
        example_xml = f.read()

    return render_template('upload/upload.html',
            form=form, example_xml=example_xml)