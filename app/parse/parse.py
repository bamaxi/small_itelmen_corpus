# from app import models
from bs4 import BeautifulSoup

big_file='ITL_IPA_texts.xml'
file='test.xml'
with open(file, 'r', encoding='utf-8') as f:
    # content = f.read()
    soup = BeautifulSoup(f, "lxml-xml")

first_text = soup.find_all('interlinear-text')[0]
first_text_pars = first_text.find_all('paragraph')
print('paragraphs total:' len(first_text_pars))

first_text_first_par = first_text_pars[0]
for i, word in enumerate(first_text_first_par.phrases.word.words.find_all('word')):
        print(f'word {i}, {word.prettify()}')

print(f'translation: {first_text_first_par.phrases.word.item}')


# брать только
