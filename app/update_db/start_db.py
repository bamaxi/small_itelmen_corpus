from app import db, create_app

app = create_app()
app.app_context().push()

from app.models import Text, Paragraph, Phrase, Word, Morph

from app.update_db.update import add_data

BASE_FILE = 'xml_texts/text_1.xml'


def add_data_from_file(file=BASE_FILE):
    if file==BASE_FILE:
        cont = input('Adding base file, continue? (y/n)')
        if cont != 'y':
            return

    add_data(file)
