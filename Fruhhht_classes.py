import threading, secrets, sqlite3

DEBUG_MODE = True
BOT_INTERVAL = 10  # in seconds
DB_NAME = secrets.db_name

class Fruhhht_bot():
    """Класс для группы"""

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

        self.bot_timer = threading.Timer(BOT_INTERVAL, self.bot_activity())
        if DEBUG_MODE:
            print(self.bot, self.chat_id, self.bot_timer)

    def start(self):
        pass

    def bot_activity(self):
        pass

    def select_from_db(self, sql_text):
        with SQL() as sql:
            return sql.fetchall(sql_text)

    def insert_into_db(self, sql_text):
        with SQL() as sql:
            return sql.insert(sql_text)


class SQL():
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


