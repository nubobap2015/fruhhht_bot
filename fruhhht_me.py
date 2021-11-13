import telebot, secrets

bot = telebot.TeleBot(secrets.bot_token)
bot_list = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    id_chat = message.chat.id
    bot = bot_list.get(id_chat)
    if bot :
        pass
    else:
        bot.start()


@bot.message_handler()
def get_text_messages(message):
    pass


print(f'{secrets.bot_name} запущен...')
bot.polling(none_stop=True, interval=0)
print(f'{secrets.bot_name} завершен...')
