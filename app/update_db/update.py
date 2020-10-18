from app.update_db.parse import parse_xml

from sqlalchemy.orm import sessionmaker, scoped_session
from app.models import Text, Paragraph, Phrase, Word, Morph
from app import db

BASE_FILE = 'xml_texts/text_1.xml'


def add_data(file):
    # used to check existence before adding
    unique_in_file = set()
    count_unique = 0
    count_total = 0

    data = parse_xml(file)
    count_total = len(list(data.keys()))

    # TODO: bad practice? should be external to func call?
    engine = db.session.get_bind()
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    session = Session()

    for title, actual_paragraphs in data.items():
        if Text.query.filter(Text.title == title).first() is not None:
            # текст с таким заголовком уже есть
            continue

        unique_in_file.add(title)
        new_text = Text(title=title)

        # при создании я связывал объекты, так что, у более высокого в иерархии
        # есть список более низких
        # как только мы создаём инстанс класса, можно переходить вниз по иерархии
        paragraphs_to_add = new_text.paragraphs
        for actual_paragraph in actual_paragraphs:
            new_par = Paragraph()
            # print('par', actual_paragraph)
            # теперь добавим всё нужное в параграф
            phrases_to_add = new_par.phrases
            for actual_phrase in actual_paragraph:
                # print('phr', actual_phrase)
                transl= actual_phrase['transl']
                new_phrase = Phrase(transl=transl)

                actual_phrase = actual_phrase['words_with_morphs']

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

    count_unique = len(unique_in_file)
    return count_unique, count_total, unique_in_file
