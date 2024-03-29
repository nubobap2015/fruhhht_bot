import telebot, my_secrets
from Fruhhht_classes import FruhhhtBot


bot = telebot.TeleBot(my_secrets.bot_token)
bot_list = {}


@bot.message_handler(commands=['status_server'])
def welcome(message):
    print(f'STATUS_SERVER: {message.from_user.username}: {message.text}')
    print(bot_list)


@bot.message_handler(commands=['start'])
def welcome(message):
    print(f'START: {message.from_user.username}: {message.text}')
    print(type(message.chat.type))
    if message.chat.type == 'group':
        # print(message)
        id_chat = message.chat.id
        id_chat_str = str(id_chat)
        my_bot = bot_list.get(id_chat_str)
        if my_bot:
            my_bot.start()
        else:
            bot_list[id_chat_str] = FruhhhtBot(bot, id_chat)
            bot_list[id_chat_str].start()
    else:
        print('Это не группа (((( ')


@bot.message_handler(commands=['stop'])
def welcome(message):
    print(f'STOP: {message.from_user.username}: {message.text}')
    id_chat = message.chat.id
    id_chat_str = str(id_chat)
    my_bot = bot_list.get(id_chat_str)
    if my_bot:
        my_bot.stop()
        del bot_list[id_chat_str]
    else:
        pass


@bot.message_handler()
def get_text_messages(message):
    print(f'сообщение: {message.from_user.username}: {message.text}')
    id_chat = message.chat.id
    id_chat_str = str(id_chat)
    my_bot = bot_list.get(id_chat_str)
    if my_bot:
        my_bot.get_message(message)
    else:
        pass


print(f'{my_secrets.bot_name} запущен...')
bot.polling(none_stop=True, interval=0)
print(f'{my_secrets.bot_name} завершен...')
