import pymorphy2
#https://pymorphy2.readthedocs.io/en/stable/user/guide.html#inflection

# потом анализ сделаем
#from fuzzywuzzy import fuzz
#from fuzzywuzzy import process



def get_normal_form(my_word):
    '''
       Переводит слово в нормальную грамматическую форму
    '''
    morph = pymorphy2.MorphAnalyzer()
    return morph.parse(my_word)[0].normal_form

def get_in_case(my_word, my_case, lvl = 0):
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

