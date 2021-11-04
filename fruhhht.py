import telebot, secrets


bot = telebot.TeleBot(secrets.bot_token)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(f'{message.from_user.username}: {message.text}')

    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, жопа, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши 'привет', жопа!")
    else:
        bot.send_message(message.from_user.id, "Жопа, я тебя не понимаю. Напиши /help.")


bot.polling(none_stop=True, interval=0)