from app.update_db.parse import parse_xml

from sqlalchemy.orm import sessionmaker, scoped_session
from app.models import Text, Paragraph, Phrase, Word, Morph
from app import db


BASE_FILE = 'big_test.xml'

def add_starting_data(base_file):
    starting_data = parse_xml(base_file)

    engine = db.session.get_bind()
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    session = Session()

    for title, actual_paragraphs in starting_data.items():
        new_text = Text(title=title)

        # при создании я связывал объекты, так что, у более высокого в иерархии
        # есть список более низких
        # как только мы создаём инстанс класса, можно переходить вниз по иерархии

        # text.paragraphs = []
        paragraphs_to_add = new_text.paragraphs
        for actual_paragraph in actual_paragraphs:
            new_par = Paragraph()

            # теперь добавим всё нужное в параграф
            phrases_to_add = new_par.phrases
            for actual_phrase in actual_paragraph:
                new_phrase = Phrase()

                # print('phr', actual_phrase)

                # добавим слова в фразу
                words_to_add = new_phrase.words
                for actual_word in actual_phrase:
                    to_words = actual_word['to_words']
                    to_morphs = actual_word['to_morphs']
                    word = Word(**to_words)

                    morphs = [Morph(**item) for item in to_morphs]
                    word.morphs = morphs

                    words_to_add.append(word)

                phrases_to_add.append(new_phrase)

            paragraphs_to_add.append(new_par)

        session.add(new_text)

    session.commit()
    Session.remove()


add_starting_data(BASE_FILE)

