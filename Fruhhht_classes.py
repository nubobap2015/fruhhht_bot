import threading, secrets, sqlite3, telebot, json
from random import choice as random_chose


DEBUG_MODE = True
BOT_INTERVAL = 10  # in seconds
BOT_DEFAULT_ALCO_HOURS = 12
DB_NAME = secrets.db_name


class FruhhhtBot():
    """Класс для группы"""

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.chat = self.bot.get_chat(self.chat_id)
        self.bot_timer = threading.Timer(BOT_INTERVAL, self._bot_activity)
        self.alko_lvl = self.get_alko_lvl()
        self.fav_drink_id = None
        self.fav_drink_name = None
        self.fav_measure_unit_id = None
        self.fav_measure_unit_name = None
        self.fav_measure_unit_vol2 = None
        self.set_fav_drink()
        if DEBUG_MODE:
            self.send_message(f'Уровень алкоголя - {self.alko_lvl}')
            print(self.bot, self.chat_id, self.bot_timer, self.alko_lvl, self)

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
        msg = message.text
        if secrets.bot_name in msg: #'@fruhhhtbot'
            percent_start = msg.find('%%')
            if percent_start >= 0:
                if len(msg[percent_start:]) == 2:
                    self.send_message(f"Аттрибуты: {self.__dict__}")
                else:
                    self.send_message(f"Аттрибут {msg[percent_start+2:]}: "
                                      f"{getattr(self,msg[percent_start+2:],'не существует')}")
            else:
                self.send_message(f"Уровень алкоголя в крови: {self.get_alko_lvl()}")
                self.drink()
                self.drink(2,3)
                self.send_message(f"Уровень алкоголя в крови: {self.get_alko_lvl()}")
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

    def drink(self, id_drink=None, id_measure_unit=None):
        """
        Бот выпивает )))
        :param id_drink: id напитка из таблицы напитков (drinks), если None то
                            выбырается напиток, установленный по-умолчанию.
        :param id_measure_unit: id тары из таблицы measure_units, если None то
                            выбырается тара, установленная по-умолчанию.
        :return: None
        """
        if  bool(id_drink):
            fav_drink_id = id_drink
            res = self._select_from_db(f"select name from drinks where id_drink = {fav_drink_id}")
            fav_drink_name = res[0][0]
        else:
            fav_drink_id = self.fav_drink_id
            fav_drink_name = self.fav_drink_name

        if bool(id_measure_unit):
            fav_measure_unit_id = id_measure_unit
            res = self._select_from_db(f"select name, vol2 from measure_units where id_measure_units = {fav_measure_unit_id}")
            print(res)
            fav_measure_unit_name = res[0][0]
            fav_measure_unit_vol2 = res[0][1]
        else:
            fav_measure_unit_id = self.fav_measure_unit_id
            fav_measure_unit_name = self.fav_measure_unit_name
            fav_measure_unit_vol2 = self.fav_measure_unit_vol2
        # ДОПИСЫВАТЬ ТУТ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # ДОПИСЫВАТЬ ТУТ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # ДОПИСЫВАТЬ ТУТ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # ДОПИСЫВАТЬ ТУТ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # записать что выпил
        # self._insert_into_db(f"insert into actions_log (id_user, id_chat, id_action, text , alko_diff, id_parent_action"
        #                     f", to_user, to_user) "
        #                     f"VALUES (1, {self.chat_id}, 1, '', {}, NULL, 1, 0)")
        # прокомментировать в чатик

    def get_drink_text(self, id_drink):
        """
        Возвращает текст комментария после выпитого напитка. В зависимости от уровня алкоголя в крови и типа напитка
        :param id_drink: id напитка из таблицы напитков (drinks)
        :return: текст комментрия после выпивки
        """
        # Сделать таблицу ответов в БД
        # Сделать выбора ответов
        return "Ухх"

    def set_fav_drink(self, id_drink=None):
        """
        Устанавливает в экземпляре класса напиток и тару по-умолчанию
        :param id_drink: id напитка из таблицы напитков (drinks), если пустое то выбырается случайный напиток
        :return: None
        """
        print('set_fav_drink')
        if id_drink:
            res = list(self._select_from_db(f"select id_drink, name from drinks where id_drink={id_drink};"))
        else:
            res = list(random_chose(self._select_from_db(f"select id_drink, name from drinks;")))
        self.fav_drink_id = res[0]
        self.fav_drink_name = res[1]
        # Возвращает случайным образом тару для напитка, причем из набора: дефолтная + все что меньше по объёму
        # Почему так? - хз просто так сделал )))
        res.append(list(random_chose(self._select_from_db(f"select distinct c.*, c.vol2 / b.vol2 from drinks a "
                                                f"join measure_units b on a.id_measure_unit=b.id_measure_units "
                                                f"join measure_units c on b.vol2 >= c.vol2 "
                                                f"where a.id_drink = {self.fav_drink_id} "
                                                f"order by c.vol2 / b.vol2 desc;"))))
        self.fav_measure_unit_id = res[2][0]
        self.fav_measure_unit_name = res[2][1]
        self.fav_measure_unit_vol2 = res[2][3]
        self._insert_into_db(f"insert into actions_log (id_user, id_chat, id_action, text , alko_diff, id_parent_action"
                             f", to_user, to_user) "
                             f"VALUES (1, {self.chat_id}, 2, '{str(json.dumps(res))}', 0, NULL, 1, 0)")

    def get_alko_lvl(self, hours=BOT_DEFAULT_ALCO_HOURS):
        """
            Возвращает уровель опьянения бота.
            hours - за какой период возвращать данные, в часах, 0->за весь период
        """
        SQLtext = f"select sum(alko_diff) from actions_log " \
                  f"where id_chat = {self.chat_id} " \
                  f"and ({hours}=0 or created_at>date('now','-{hours} hours'));"
        # print(SQLtext)
        alko_lvl = self._select_from_db(SQLtext)[0][0]
        return 0 if alko_lvl == None else alko_lvl

    def _update_chat_in_db(self):
        res = self._select_from_db(f"select * from chats where id_chat = {self.chat_id};")
        if len(res) > 0:
            return self._update_db(f"update chats set name='{self.chat.title}' where id_chat = {self.chat_id};")
        else:
            return self._insert_into_db(f"insert into chats (id_chat, name) "
                                        f"values ({self.chat_id},'{self.chat.title}');")

    def _bot_activity(self):
        """ Активность чат бота"""
        self.check_chat_in_db()
        self.alko_lvl = self.get_alko_lvl()
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
