import os
from app import db, create_app

app = create_app()
app.app_context().push()

from app.update_db.update import add_data


BASE_FILE = 'xml_texts/text_1.xml'


def add_data_from_file(file=BASE_FILE):
    if file == BASE_FILE:
        print(f'Executing `flask db migrate` and adding base file ({file})')
        # cont = input(f'Executing `flask db migrate` and adding base file ({file})')
        # if cont != 'y':
        #     return
        os.system('flask db upgrade')
        os.system('flask db migrate')

        add_data(file)


add_data_from_file()