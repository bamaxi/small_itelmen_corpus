from bs4 import BeautifulSoup


def phrases_to_dicts(phrases):
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
    for word_tag in word_tags:
        word_dict = {'to_words': {}, 'to_morphs': []}
        word = word_tag

        # TODO: check possible configurations. When is <morphemes> missing?
        #  Are there cases when it's missing and <word type='txt'> is present?
        try:
            morphemes_tag = word.morphemes.extract()
        except AttributeError as e:
            # tag <word> doesn't have a nested <morphemes>
            continue

        # find a word and add it with its position if it's found
        #     punctuation is omitted, because its type is (should be) `punct`
        word_text = word.find('item', type='txt').string
        # word_dict['to_words']['text'] = word.find('item', type='txt').string
        if word_text:
            word_dict['to_words']['text'] = word_text
            word_dict['to_words']['position'] = order
            order += 1
        # try to get a translation and part of speech.
        try:
            word_dict['to_words']['transl'] = word.find('item', type='gls').string
            word_dict['to_words']['pos'] = word.find('item', type='pos').string
        except AttributeError as e:
            pass

        # get all <morphemes> data for current word
        for morph in morphemes_tag.find_all('morph'):
            morph_dict = {}
            morph_dict['type'] = morph.get('type', '')
            morph_dict['text'] = morph.find('item', type='txt').string

            try:
                morph_dict['base_form'] = morph.find('item', type='cf').string
                morph_dict['gloss'] = morph.find('item', type='gls').string
            except AttributeError as e:
                pass

            word_dict['to_morphs'].append(morph_dict)

        # build full gloss from relevant morph glosses
        full_gloss = ''
        for morph in word_dict['to_morphs']:
            try:
                full_gloss += morph.get('gloss') + '-'
            except TypeError:
                # something is None and we're concatenating None + str
                continue
        word_dict['to_words']['gloss'] = full_gloss.rstrip('-')

        words_with_morphs.append(word_dict)

    # get phrase translation
    try:
        transl = phrases.find('item', type='gls').string
    except AttributeError:
        pass
    if transl is None:
        transl = '(перевода нет)'
        # чтобы была правильная вложенность []
        # TODO: make data structure simpler
    return [{'transl': transl, 'words_with_morphs': words_with_morphs}]


def paragraphs_to_dict(paragraphs, take_first_paragraph=False):
    if take_first_paragraph:
        paragraphs = paragraphs[0]
    return [phrases_to_dicts(paragraph.phrases)
                for paragraph in paragraphs]


def parse_xml(filename, take_first_text=False, take_first_paragraph=False):
    """
    parses an .xml file in Verifiable generic XML markup exported from Fieldworks
    :param filename:
    :param take_first_text: only parse first text in file (for testing)
    :param take_first_paragraph: only parse first paragraph in file (for testing)
    :return:
    """

    res = {}  # here parsed text will be stored in hierarchical fashion
    par_count = 0

    with open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, "lxml-xml")

    # find texts, count them, print soup if no texts found
    texts = soup.find_all('interlinear-text')
    total_texts = len(texts)
    print(f"texts by <interlinear-text>: {total_texts}")
    if total_texts == 0:
        print(f"no texts found, soup is:\n {soup.prettify()}")

    # TODO: better code that should first be tested
    if take_first_text:
        texts = [texts[0]]

    # ... *here we would have code currenly in "else" clause* ...
    # END_TODO

    if take_first_text:
        paragraphs = texts[0].find_all('paragraph')
        try:
            title = texts[0].find('item', type='title').string
        except AttributeError as e:
            title = 'Неизвестный текст'
        res[title] = paragraphs
        par_count = len(paragraphs)
    else:
        for i, text in enumerate(texts):
            paragraphs = text.find_all('paragraph')
            try:
                title = text.find('item', type='title').string
            except AttributeError as e:
                title = str(i)
            res[title] = paragraphs

            par_count += len(paragraphs)

    print(f'take_first_text is {take_first_text}, total {par_count} found')

    # print(list(res.keys()), len(texts))
    for title, paragraphs in res.items():
        res[title] = paragraphs_to_dict(paragraphs, take_first_paragraph=take_first_paragraph)

    return res
