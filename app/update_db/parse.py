import typing as T
import logging

import bs4
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


VALUE_UNKNOWN = "0"
SOURCE_UNKNOWN = "(источник неизвестен)"
MORPH_SEP = "-"


class DefaultString:
    string = VALUE_UNKNOWN


def safe_find_get_string(
    base_tag: bs4.Tag, search_tag: str, uknown_value_repl: str = VALUE_UNKNOWN,
    **query: T.Dict[str, T.Any]
) -> T.Union[bs4.NavigableString, str]:
    res = base_tag.find(search_tag, **query)
    if res:
        return res.string or uknown_value_repl
    return uknown_value_repl


def phrases_to_dicts(phrases: bs4.Tag, paragraph_i: int):
    """
    turn what's inside <phrases> - <word> that contains
        <words> - words themselves
        and <item> - text segment mark
    into list of dicts - list of words
    In sample text paragraph always contained <phrases> which contained <word> that contained <words>.
    Searching all words, just in case, requires looking for immediate <word> descendant of phrases
    :return: dict with phrase translation, and words with their morphs
    """
    words_with_morphs = []
    words = phrases.word.words.extract()
    word_tags = words.find_all('word')

    order = 1
    for i, word_tag in enumerate(word_tags):
        to_words = {}
        to_morphs = []
        word_dict = {'to_words': to_words, 'to_morphs': to_morphs}
        word = word_tag

        word_text = safe_find_get_string(word, 'item', type='txt')
        # word_dict['to_words']['text'] = word.find('item', type='txt').string
        if word_text == VALUE_UNKNOWN and not word.find("item", type="punct"):
            logger.error(f"tag <word> doesn't have <item>: "
                         f"word {word} (i={i}) (paragraph_i={paragraph_i})")

        # TODO: check possible configurations. When is <morphemes> missing?
        #  Are there cases when it's missing and <word type='txt'> is present?
        try:
            morphemes_tag = word.morphemes.extract()
        except AttributeError as e:
            logger.debug(
                f"tag <word> doesn't have a nested <morphemes>: word {word_text} "
                f"(paragraph_i={paragraph_i})"
            )
            continue

        # find a word and add it with its position if it's found
        #     punctuation is omitted, because its type is (should be) `punct`
        if word_text:
            word_dict['to_words']['text'] = word_text
            word_dict['to_words']['position'] = order
            order += 1
        # try to get a translation and part of speech.
        # try:
        #     word_dict['to_words']['transl'] = word.find('item', type='gls').string
        #     word_dict['to_words']['pos'] = word.find('item', type='pos').string
        # except AttributeError as e:
        #     pass
        word_dict['to_words']['transl'] = safe_find_get_string(word, 'item', type='gls')
        word_dict['to_words']['pos'] = safe_find_get_string(word, 'item', type='pos')

        # get all <morphemes> data for current word
        for morph in morphemes_tag.find_all('morph'):
            morph_dict = {}
            morph_dict['type'] = morph.get('type', VALUE_UNKNOWN)
            morph_dict['text'] = safe_find_get_string(morph, 'item', type='txt')

            # try:
            #     morph_dict['base_form'] = morph.find('item', type='cf').string
            #     morph_dict['gloss'] = morph.find('item', type='gls').string
            # except AttributeError as e:
            #     pass
            morph_dict['base_form'] = safe_find_get_string(morph, 'item', type='cf')
            morph_dict['gloss'] = safe_find_get_string(morph, 'item', type='gls')

            word_dict['to_morphs'].append(morph_dict)

        # build full gloss from relevant morph glosses
        # full_gloss = ''
        # for morph in word_dict['to_morphs']:
        #     try:
        #         full_gloss += morph.get('gloss') + '-'
        #     except TypeError:
        #         # something is None and we're concatenating None + str
        #         continue
        # word_dict['to_words']['gloss'] = full_gloss.rstrip('-')
        full_gloss = MORPH_SEP.join([morph["gloss"] for morph in word_dict["to_morphs"]])
        word_dict['to_words']['gloss'] = full_gloss
        words_with_morphs.append(word_dict)

    # get phrase translation
    # try:
    #     transl = phrases.find('item', type='gls').string
    # except AttributeError:
    #     pass
    # if transl is None:
    transl = safe_find_get_string(phrases, 'item', type='gls')
    if transl == VALUE_UNKNOWN:
        transl = '(перевода нет)'
        # чтобы была правильная вложенность []
        # TODO: make data structure simpler
    return [{'transl': transl, 'words_with_morphs': words_with_morphs}]


def paragraphs_to_dict(paragraphs, take_first_paragraph=False):
    if take_first_paragraph:
        paragraphs = [paragraphs[0]]
    return [phrases_to_dicts(paragraph.phrases, i)
            for i, paragraph in enumerate(paragraphs)]


def parse_xml(filename, take_first_text=False, take_first_paragraph=False):
    """
    parses an .xml file in Verifiable generic XML markup exported from Fieldworks
    :param filename:
    :param take_first_text: only parse first text in file (for testing)
    :param take_first_paragraph: only parse first paragraph in file (for testing)
    :return:
    """
    logger.debug(f"processing file `{filename}` with "
                 f"take_first_text={take_first_text}, "
                 f"take_first_paragraph={take_first_paragraph}")

    res = {}  # here parsed text will be stored in hierarchical fashion
    par_count = 0

    with open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, "lxml-xml")

    if not soup:
        logger.warning(f"soup is empty for file `{filename}`")
        return res

    # find texts, count them, print soup if no texts found
    texts = soup.find_all('interlinear-text')
    total_texts = len(texts)
    logger.info(f"texts by <interlinear-text>: {total_texts}")
    if total_texts == 0:
        logger.warning(f"no texts found in soup for file `{filename}`")
        logger.debug(f"soup was:\n {soup.prettify()}")
        # print(f"no texts found, soup is:\n {soup.prettify()}")

    # TODO: better code that should first be tested
    if take_first_text:
        logger.debug(f"taking first text only")
        texts = [texts[0]]

    logger.debug(f"texts: {texts}")

    # ... *here we would have code currenly in "else" clause* ...
    # END_TODO

    # if take_first_text:
    #     paragraphs = texts[0].find_all('paragraph')
    #     logger.debug(paragraphs[0])
    #     try:
    #         title = texts[0].find('item', type='title').string
    #     except AttributeError as e:
    #         title = 'Неизвестный текст'
    #     res[title] = paragraphs
    #     par_count = len(paragraphs)
    # else:
    for i, text in enumerate(texts):
        paragraphs = text.find_all('paragraph')
        try:
            title = (
                text.find('item', type='title', lang='ru')
                or text.find('item', type='title')
            ).string
        except AttributeError as e:
            title = f"(Неизвестный текст - {i})"
        res[title] = {"par": paragraphs}

        maybe_source = text.find('item', type="source")
        if maybe_source:
            source = maybe_source.string
        else:
            source = SOURCE_UNKNOWN
        res[title]["source"] = source

        par_count += len(paragraphs)

    logger.info(f'take_first_text is {take_first_text}, total {par_count} paragraphs found')

    # print(list(res.keys()), len(texts))
    for title, data in res.items():
        paragraphs = data["par"]
        res[title]["par"] = paragraphs_to_dict(paragraphs, take_first_paragraph=take_first_paragraph)

    return res
