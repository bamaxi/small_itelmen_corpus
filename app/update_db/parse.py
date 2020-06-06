from bs4 import BeautifulSoup


def phrases_to_dicts(phrases):
    '''
    turn what's inside <phrases> - <word> that contains
        <words> - words themselves
        and <item> - text segment mark
    into list of dicts - list of words
    In sample text paragraph always contained <phrases> which contained <word> that contained <words>.
    Searching all words, just in case, requires looking for immediate <word> descendant of phrases
    :return:
    '''
    words_with_morphs = []
    words = phrases.word.words.extract()
    word_tags = words.find_all('word')
    # word_tags = phrases.word.words.find_all('word')
    for word_tag in word_tags:
        word_dict = {'to_words': {}, 'to_morphs': []}
        word = word_tag

        try:
            morphemes_tag = word.morphemes.extract()
        except AttributeError as e:
            continue

        word_dict['to_words']['text'] = word.find('item', type='txt').string
        try:
            word_dict['to_words']['transl'] = word.find('item', type='gls').string
            word_dict['to_words']['pos'] = word.find('item', type='pos').string
        except AttributeError as e:
            pass

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

        words_with_morphs.append(word_dict)
        # print(words_with_morphs)

    try:
        transl = phrases.find('item', type='gls').string
    except AttributeError:
        pass
    if transl is None:
        transl = '?'
        # чтобы была правильная вложенность []
    return [{'transl': transl, 'words_with_morphs': words_with_morphs}]


def paragraphs_to_dict(paragraphs, take_first_paragraph=False):
    if take_first_paragraph:
        paragraphs = paragraphs[0]
    return [phrases_to_dicts(paragraph.phrases)
                for paragraph in paragraphs]

def parse_xml(filename, take_first_text=False, take_first_paragraph=False):
    res = {}
    par_count = 0

    with open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, "lxml-xml")

    texts = soup.find_all('interlinear-text')
    print(len(texts))
    if take_first_text==True:
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
