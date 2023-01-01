import pymorphy2
import pymystem3
from my_secrets import NN_LOGIN, NN_PASSWORD
import requests
from sklearn.feature_extraction.text import TfidfVectorizer

'''
NN_IPADRESS = '0.0.0.0'
NN_PORT = 5000
NN_COMMANDS = [['GET', '/chatbot/about'],           #0
               ['GET', '/chatbot/questions'],       #1
               ['POST','/chatbot/speech-to-text'],  #2
               ['POST','/chatbot/text-to-speech'],  #3
               ['POST','/chatbot/text-to-text'],    #4
               ]

# https://pymorphy2.readthedocs.io/en/stable/user/guide.html#inflection

# потом анализ сделаем
# from fuzzywuzzy import fuzz
# from fuzzywuzzy import process



def get_cb_request(r_type=get_cb_request_TYPE_and_URL(0)[0],
                   r_adr=get_cb_request_TYPE_and_URL(0)[1],
                   r_data={text: 'привет'},
                   auth='Basic0'
                   ):
    r = requests.get(adr,)


def get_cb_quest():
    #/chatbot/questions
'''

def get_normal_form(my_word):
    '''
       Переводит слово в нормальную грамматическую форму
    '''
    morph = pymorphy2.MorphAnalyzer()
    return morph.parse(my_word)[0].normal_form


def get_in_case(my_word, my_case, lvl=0):
    '''
    Переводит слово в какую-то грамматическую форму.
    Лексемы смотри тут https://pymorphy2.readthedocs.io/en/stable/user/grammemes.html#

    :param my_word: Само слово
    :param my_case: лексема {'gent'}
    :param lvl: по-умолчанию = 0, есле у слова есть несколько значений можно выбрать другое
    :return: Строка. Слово в нужной форме
    '''
    morph = pymorphy2.MorphAnalyzer()
    my_morph = morph.parse(my_word)[lvl]
    ret = my_morph.inflect(my_case).word
    return ret


def get_ya_lemmas(atext: str) -> list:
    '''
    Возвращает словарь лексемм от Yandex

    :param atext: Исходный текст
    :return: Список лексемм
    '''
    m = pymystem3.Mystem()
    return m.lemmatize(atext)


def my_vectorizer(atext):
    my_vector = TfidfVectorizer()
    vector = my_vector.fit_transform(atext)
    return vector

