import telebot, secrets, sqlite3, datetime, semantic


bot = telebot.TeleBot(secrets.bot_token)
conn = sqlite3.connect('myAlcoFriends.sqlite')
cursor = conn.cursor()


def get_db_user(user_id, user_name, cursor=cursor, conn=conn):
    #print(user_id, cursor)
    cursor.execute(f'select * from users where id_user = {user_id}')
    results = cursor.fetchall()
    if len(results) == 0:
        print(f'Пользователь {user_id}:{user_name} не опознан. Добавляю в БД...')
        cursor.execute(f'insert into users (id_user, name, created_at) values '
                       f'({user_id}, "{user_name}" , {datetime.datetime.now().timestamp()});')
        conn.commit()
        results = get_db_user(user_id, user_name, cursor=cursor, conn=conn)
    if results[0][2] != user_name:
        print('Ты чё? Ник сменил??')
    print(type(results))
    return results


# @bot.message_handler(content_types=['text'])
@bot.message_handler()
def get_text_messages(message):
    print(f'{message.from_user.username}: {message.text}')
    print(f'{message}')
    get_db_user(message.from_user.id, message.from_user.username)
    bot.send_message(message.chat.id, f"Привет, @{message.from_user.username}, чем я могу тебе помочь?")




print(f'Бот {secrets.bot_name} запущен...')
#bot.polling(none_stop=True, interval=0)
print(get_db_user(1111111, 'mamamama2'))
print(semantic.get_normal_form('ромом'))
print(semantic.get_in_case('ромом', {'gent'}))
conn.close()