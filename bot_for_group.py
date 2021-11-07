import fruhhht


@fruhhht.bot.message_handler()
def get_text_messages(message):
    print(f'{message.from_user.username}: {message.text}')




