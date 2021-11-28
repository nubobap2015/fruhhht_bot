import threading, secrets, sqlite3, telebot

DEBUG_MODE = True
BOT_INTERVAL = 10  # in seconds
DB_NAME = secrets.db_name


class FruhhhtBot():
    """Класс для группы"""

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.chat = self.bot.get_chat(self.chat_id)
        self.bot_timer = threading.Timer(BOT_INTERVAL, self._bot_activity)
        if DEBUG_MODE:
            print(self.bot, self.chat_id, self.bot_timer)

    @property
    def is_run(self):
        return self.bot_timer.is_alive()

    def start(self):
        if self.is_run:
            self.send_message('Уже запущен')
        else:
            self.send_message('Запуск бота')
            self.bot_timer.start()

    def stop(self):
        if self.is_run:
            self.send_message('Остановка бота')
            self.bot_timer.cancel()
        else:
            self.send_message('Уже остановлен')

    def get_message(self, message):
        pass

    def send_message(self, text_message):
        self.bot.send_message(self.chat_id, text_message)

    def check_chat_in_db(self):
        res = self._select_from_db(f"select * from chats where id_chat = {self.chat_id};")
        if len(res) > 0:
            print(res)
        else:
            print('Чат не найден в БД')
            self._update_chat_in_db()

    def _update_chat_in_db(self):
        res = self._select_from_db(f"select * from chats where id_chat = {self.chat_id};")
        if len(res) > 0:
            return self._update_db(f"update chats set name='{self.chat.title}' where id_chat = {self.chat_id};")
        else:
            return self._insert_into_db(f"insert into chats (id_chat, name) values ({self.chat_id},'{self.chat.title}');")

    def _bot_activity(self):
        """ Активность чат бота"""
        self.check_chat_in_db()
        self.bot.send_message(self.chat_id, f"Активность")
        self.bot_timer = threading.Timer(BOT_INTERVAL, self._bot_activity)
        self.bot_timer.start()

    @staticmethod
    def _select_from_db(sql_text):
        with SQL() as sql:
            return sql.fetchall(sql_text)

    @staticmethod
    def _insert_into_db(sql_text):
        with SQL() as sql:
            return sql.insert(sql_text)

    @staticmethod
    def _update_db(sql_text):
        with SQL() as sql:
            return sql.update(sql_text)


class SQL:
    """ Сиквел обертка для обращений к БД SQLite"""
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, type, value, traceback):
        # Exception handling here
        self.cur.close()
        self.conn.close()

    def fetchall(self, sql):
        return self.cur.execute(sql).fetchall()

    def insert(self, sql):
        self.cur.execute(sql)
        ins_id = self.cur.lastrowid
        self.conn.commit()
        return ins_id

    def update(self, sql):
        self.cur.execute(sql)
        self.conn.commit()
        return True
