import telebot, secrets, sqlite3, datetime, semantic

#Constants
USER_ALKO_TIME_IN_HOURS = 8


bot = telebot.TeleBot(secrets.bot_token)


def get_db_user(message):
    my_conn = sqlite3.connect(secrets.db_name)
    cursor = my_conn.cursor()
    cursor.execute(f'select * from users where id_user = {message.from_user.id}')
    results = cursor.fetchall()
    if len(results) == 0:
        print(f'Пользователь {message.from_user.id}:{message.from_user.username} не опознан. Добавляю в БД...')
        cursor.execute(f'insert into users (id_user, name) values '
                       f'({message.from_user.id}, "{message.from_user.username}");')
        my_conn.commit()
        results = get_db_user(message)
    if results[0][2] != message.from_user.username and len(results[0][2]) >0:
        print('Ты чё? Ник сменил??')
    my_conn.close()
    return results


def get_db_chat(message):
    my_conn = sqlite3.connect(secrets.db_name)
    cursor = my_conn.cursor()
    cursor.execute(f'select * from chats where id_chat = {message.chat.id}')
    results = cursor.fetchall()
    if len(results) == 0:
        print(f'Чат {message.chat.id}:{message.chat.title} не опознан. Добавляю в БД...')
        cursor.execute(f'insert into chats (id_chat, name) values '
                       f'({message.chat.id}, "{message.chat.title}");')
        my_conn.commit()
        results = get_db_chat(message)
    if results[0][1] != message.chat.title and len(results[0][1]) > 0:
        print('Тему сменили??')
    my_conn.close()
    return results


def write_to_log(id_action, id_user, id_chat, text, alko_diff, to_user, toxic_diff=0, id_parent_action='null'):
    my_conn = sqlite3.connect(secrets.db_name)
    cursor = my_conn.cursor()
    cursor.execute(f"insert into actions_log (id_user,id_chat,id_action,text,alko_diff,"
                   f"id_parent_action,to_user,toxic_diff) values "
                   f"({id_user},{id_chat},{id_action},'{text}',{alko_diff},"
                   f"{id_parent_action},{to_user},{toxic_diff});")
    ins_id = cursor.lastrowid
    my_conn.commit()
    my_conn.close()
    return ins_id


def get_user_state(id_user, id_chat=0):
    my_conn = sqlite3.connect(secrets.db_name)
    cursor = my_conn.cursor()
    my_chat = f'and id_chat = {id_chat}'
    my_query = f'select id_user, sum(alko_diff) as alko_lvl, sum(toxic_diff) as toxic_lvl ' \
               f'from actions_log where id_user = {id_user} ' \
               f'{my_chat if id_chat != 0 else ""}'
    print(my_query)
    cursor.execute(my_query);
    ret = cursor.fetchall()
    my_conn.commit()
    my_conn.close()
    return ret


@bot.message_handler()
def get_text_messages(message):
    print(f'{message.from_user.username}: {message.text}')
    # print(f'{message}')
    get_db_user(message)
    get_db_chat(message)
    bot.send_message(message.chat.id, f"Привет, @{message.from_user.username}, чем я могу тебе помочь?")


#  write_to_log(1,1,1,'dd',0,1,5)
print(get_user_state(1))
print(get_user_state(10,4))
print(get_user_state(144,0))

print(f'{secrets.bot_name} запущен...')
# bot.polling(none_stop=True, interval=0)
print(f'{secrets.bot_name} завершен...')
'''
print(get_db_user(1111111, 'mamamama2'))
print(semantic.get_normal_form('ромом'))
print(semantic.get_in_case('ромом', {'gent'}))
'''
