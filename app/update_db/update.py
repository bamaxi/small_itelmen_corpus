import argparse
import logging
import os
from pathlib import Path
import typing as T


from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, scoped_session

import app.update_db.parse as parse_module
from app.update_db.parse import parse_xml
from app.models import Text, Paragraph, Phrase, Word, Morph
from app import create_app, db


logger = logging.getLogger(__name__)


BASE_DIR = Path("texts/")
BASE_FILE = next(BASE_DIR.glob("*.xml"))


Report = T.Dict[str, T.Union[int, set[str]]]


def add_file_data(filename: T.Union[str, Path]) -> Report:
    # used to check existence before adding
    unique_in_file = set()
    count_unique = 0
    count_total = 0

    logger.info(f"adding data from file: {filename}")
    data = parse_xml(filename)
    count_total = len(data)

    logger.info(f"text titles in the file: {list(data)}")

    session = db.session
    # session = Session()
    for title, data in data.items():
        actual_paragraphs = data["par"]
        # with session() as session:
        stmt = select(Text).where(Text.title == title)
        if session.execute(stmt).first() is not None:
            # текст с таким заголовком уже есть
            continue

        unique_in_file.add(title)
        new_text = Text(title=title, source=data["source"])

        # при создании я связывал объекты, так что, у более высокого в иерархии
        # есть список более низких
        # как только мы создаём инстанс класса, можно переходить вниз по иерархии
        paragraphs_container = new_text.paragraphs
        for actual_paragraph in actual_paragraphs:
            new_par = Paragraph()
            # print('par', actual_paragraph)
            # теперь добавим всё нужное в параграф
            phrases_to_add = new_par.phrases
            for actual_phrase in actual_paragraph:
                # print('phr', actual_phrase)
                transl = actual_phrase['transl']
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

            paragraphs_container.append(new_par)

        session.add(new_text)

    session.commit()
    logger.info(f"data commited")
    # Session.remove()

    count_unique = len(unique_in_file)
    return {
        "count_unique": count_unique, "count_total": count_total,
        "unique_in_file": unique_in_file
    }


def add_folder_data(
        folder: T.Union[str, Path], extension: T.Union[str, None]="xml"
) -> T.List[Report]:
    logger.info(f"adding files from a folder: {folder}")

    if not isinstance(folder, Path):
        folder = Path(folder)
    
    if extension is None:
        file_iter = (item for item in folder.iterdir() if item.is_file())
    else:
        file_iter = folder.glob(f"*.{extension}")
    
    results = []
    for i, file in enumerate(file_iter):
        _file_res = add_file_data(file)
        file_res = {"i": i, "filename": file, **_file_res}
        results.append(file_res)
    
    results_str = "\n".join(str(res) for res in results)
    logger.info(f"results for files:\n{results_str}")
    
    return results


def set_parse_logging(level: T.Union[str, int]):
    logging.getLogger(parse_module.__name__).setLevel(level)


MODE_ADD = "add"


def make_argparser(prog_name: T.Optional[str]=None, description: T.Optional[str]=None):
    parser = argparse.ArgumentParser(
        prog_name or Path(__file__).name,
        description=(
            description
            or "Parses xml texts from FieldWorks and updates the database"
        )
    )

    # parser.add_argument("mode", choices=["file", "folder", "init"],
    #                     help="evaluation mode: `init`, `file` or `folder`")
    subparsers = parser.add_subparsers(
        dest="mode",
        help="evaluation mode: `add` (default is `init`) `add` implies init is performed"
    )

    source_parser = subparsers.add_parser(MODE_ADD, help="initiate db as well as add files")
    source = source_parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", help="filename of the .xml with one or more texts")
    source.add_argument("--folder", "-d", default=BASE_DIR, help="directory with the .xml texts")

    parser.add_argument(
        "-l", "--log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )

    return parser


def prepare_db():
    print(f'Executing `flask db upgrade` and `flask db migrate`')
    os.system('flask db upgrade')
    os.system('flask db migrate')


def act_on_args(args: argparse.Namespace):
    set_parse_logging(args.log)
    logger.setLevel(args.log)

    prepare_db()

    if args.mode != MODE_ADD:
        return

    app = create_app()

    if args.file:
        dir_ = args.folder if args.folder != BASE_DIR else Path(args.folder)
        file = dir_ / args.file
        
        with app.app_context():
            out = add_file_data(file)
        print(out)

    elif args.mode:
        dir = Path(args.folder)
        
        with app.app_context():
            files_results = add_folder_data(dir)

        print(*files_results, sep="\n")



if __name__ == "__main__":
    parser = make_argparser()
    args = parser.parse_args()

    print(args)

    act_on_args(args)

