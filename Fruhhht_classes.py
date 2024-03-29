import threading, my_secrets, sqlite3, telebot, json, semantic, requests, json
from random import choice as random_chose
from random import randint

DEBUG_MODE = True
BOT_INTERVAL = 10  # in seconds
BOT_DEFAULT_ALCO_HOURS = 12
DB_NAME = my_secrets.db_name
NN_IPADRESS = '0.0.0.0'
NN_PORT = 5000
NN_COMMANDS = [['GET', '/chatbot/about'],  # 0
               ['GET', '/chatbot/questions'],  # 1
               ['POST', '/chatbot/speech-to-text'],  # 2
               ['POST', '/chatbot/text-to-speech'],  # 3
               ['POST', '/chatbot/text-to-text'],  # 4
               ]


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
        self.fav_drink_strong = None
        self.fav_drink_toxic = None
        self.fav_measure_unit_id = None
        self.fav_measure_unit_name = None
        self.fav_measure_unit_vol = None
        self.fav_measure_unit_vol2 = None
        self.nn_session = None
        # self.is_nn_auth = None
        # Установка соединения с web-сервером с нейросетью
        self.set_nn_session()
        # Установка напитка и тары
        self.set_fav_drink()
        # Приветствие в чат
        self.send_message(self.get_text_from_dict(6))
        if DEBUG_MODE:
            self.send_message2(f'_Уровень алкоголя - {self.alko_lvl}_')
            # print(self.bot, self.chat_id, self.bot_timer, self.alko_lvl, self)

    @property
    def is_run(self):
        return self.bot_timer.is_alive()

    def start(self):
        if self.is_run:
            self.send_message2('_Уже запущен_')
        else:
            self.send_message2('_Запуск бота_')
            self.bot_timer.start()

    def stop(self):
        if self.is_run:
            self.send_message2('_Остановка бота_')
            self.bot_timer.cancel()
        else:
            self.send_message2('_Уже остановлен_')

    def get_message(self, message):
        msg = message.text
        replay_user = ''
        print(message)
        if message.reply_to_message:
            replay_user = message.reply_to_message.from_user.username
        if my_secrets.bot_name in msg or replay_user==my_secrets.bot_name.removeprefix('@'):  # '@fruhhhtbot'
            percent_start = msg.find('%%')
            if percent_start >= 0:
                if len(msg[percent_start:]) == 2:
                    self.send_message(f"Атрибуты: {self.__dict__}")
                else:
                    self.send_message(f"Атрибут {msg[percent_start + 2:]}: "
                                      f"{getattr(self, msg[percent_start + 2:], 'не существует')}")
            else:
                clear_msg = msg.removeprefix('@fruhhhtbot ')
                answer = self.get_answer_from_nn(clear_msg)
                print(answer)
                self.replay_message(answer, message.id)
            if 'пей' in msg or 'выпей' in msg or 'бухн' in msg:
                self.drink(message_id=message.message_id)

    def send_message(self, text_message):
        self.bot.send_message(self.chat_id, text_message)

    def send_message2(self, text_message):
        self.bot.send_message(self.chat_id, text_message, parse_mode='Markdown')

    def replay_message(self, text_message, reply_to_message_id):
        self.bot.send_message(self.chat_id, text_message, parse_mode='Markdown', reply_to_message_id=reply_to_message_id)

    def get_dicts(self, id_type, alko_lvl=None, id_drink=None):
        if not (alko_lvl):
            alko_lvl = self.get_alko_lvl()
        SQLtext = f"select * from dict " \
                  f"where type={id_type} and alko_lvl_min<={alko_lvl} and alko_lvl_max>{alko_lvl}" \
                  f" and (id_drink is null {'or id_drink = ' + str(id_drink) if bool(id_drink) else ''});"
        return self._select_from_db(SQLtext)

    def get_dict_rnd(self, id_type, alko_lvl=None, id_drink=None):
        a = self.get_dicts(id_type, alko_lvl, id_drink)
        return random_chose(a) if len(a) > 0 else [None, None, '']

    def get_text_from_dict(self, id_type, alko_lvl=None, id_drink=None):
        return self.get_dict_rnd(id_type, alko_lvl, id_drink)[2]

    def check_chat_in_db(self):
        res = self._select_from_db(f"select * from chats where id_chat = {self.chat_id};")
        if len(res) > 0:
            print(res)
        else:
            print('Чат не найден в БД')
            self._update_chat_in_db()

    def drink(self, **kwargs):
        """
        Бот выпивает )))
        :param id_drink: id напитка из таблицы напитков (drinks), если None то
                            выбырается напиток, установленный по-умолчанию.
        :param id_measure_unit: id тары из таблицы measure_units, если None то
                            выбырается тара, установленная по-умолчанию.
        :return: None
        """
        id_drink = kwargs.get('id_drink')
        id_measure_unit = kwargs.get('id_measure_unit')
        message_id = kwargs.get('message_id', 'NULL')
        if bool(id_drink):
            fav_drink_id = id_drink
            res = self._select_from_db(f"select name, strong, toxic from drinks where id_drink = {fav_drink_id}")
            fav_drink_name = res[0][0]
            fav_drink_strong = res[0][1]
            fav_drink_toxic = res[0][2]
        else:
            fav_drink_id = self.fav_drink_id
            fav_drink_name = self.fav_drink_name
            fav_drink_strong = self.fav_drink_strong
            fav_drink_toxic = self.fav_drink_toxic

        if bool(id_measure_unit):
            fav_measure_unit_id = id_measure_unit
            res = self._select_from_db(f"select name, vol, vol2 from measure_units "
                                       f"where id_measure_units = {fav_measure_unit_id}")
            fav_measure_unit_name = res[0][0]
            fav_measure_unit_vol = res[0][1]
            fav_measure_unit_vol2 = res[0][2]
        else:
            fav_measure_unit_id = self.fav_measure_unit_id
            fav_measure_unit_name = self.fav_measure_unit_name
            fav_measure_unit_vol = self.fav_measure_unit_vol
            fav_measure_unit_vol2 = self.fav_measure_unit_vol2

        alko_diff = fav_drink_strong * fav_measure_unit_vol
        toxic_diff = fav_drink_toxic * fav_measure_unit_vol
        my_text = json.dumps([[fav_drink_id, fav_drink_name, fav_drink_strong, fav_drink_toxic],
                              [fav_measure_unit_id, fav_measure_unit_name, fav_measure_unit_vol,
                               fav_measure_unit_vol2]])
        print(my_text)
        # записать в БД что выпил
        self._insert_into_db(f"insert into actions_log (id_user, id_chat, id_action, text , alko_diff, id_parent_action"
                             f", to_user, toxic_diff) "
                             f"VALUES (1, {self.chat_id}, 1, '{my_text}', {alko_diff}, {message_id}, 1, {toxic_diff})")
        # прокомментировать в чатик
        how = semantic.get_in_case(fav_measure_unit_name, {'accs', 'sing'})
        what = semantic.get_in_case(fav_drink_name, {'gent', 'sing'})
        self.send_message2(f"{self.get_text_from_dict(4, None, fav_drink_id)} _(выпил {how} {what})_")
        self.alko_lvl = self.get_alko_lvl()

    def set_fav_drink(self, id_drink=None):
        """
        Устанавливает в экземпляре класса напиток и тару по-умолчанию
        :param id_drink: id напитка из таблицы напитков (drinks), если пустое то выбырается случайный напиток
        :return: None
        """
        if id_drink:
            res = list(self._select_from_db(f"select id_drink, name from drinks where id_drink={id_drink};"))
        else:
            res = list(random_chose(self._select_from_db(f"select id_drink, name, strong, toxic from drinks;")))
        self.fav_drink_id = res[0]
        self.fav_drink_name = res[1]
        self.fav_drink_strong = res[2]
        self.fav_drink_toxic = res[3]
        # Возвращает случайным образом тару для напитка, причем из набора: дефолтная + все что меньше по объёму
        # Почему так? - хз просто так сделал )))
        res.append(list(random_chose(self._select_from_db(f"select distinct c.*, c.vol2 / b.vol2 from drinks a "
                                                          f"join measure_units b on a.id_measure_unit=b.id_measure_units "
                                                          f"join measure_units c on b.vol2 >= c.vol2 "
                                                          f"where a.id_drink = {self.fav_drink_id} "
                                                          f"order by c.vol2 / b.vol2 desc;"))))
        print(res)
        self.fav_measure_unit_id = res[4][0]
        self.fav_measure_unit_name = res[4][1]
        self.fav_measure_unit_vol = res[4][2]
        self.fav_measure_unit_vol2 = res[4][3]
        # Запись в БД о смене напитска
        self._insert_into_db(f"insert into actions_log (id_user, id_chat, id_action, text , alko_diff, id_parent_action"
                             f", to_user, toxic_diff) "
                             f"VALUES (1, {self.chat_id}, 2, '{str(json.dumps(res))}', 0, NULL, 1, 0)")
        # Сообщение в чат о выборе напитка
        phrase_tuple = self.get_dict_rnd(5)
        how = semantic.get_in_case(self.fav_drink_name, {phrase_tuple[1]})
        phrase = str(phrase_tuple[2]).replace('%%drink_name%%', how)
        self.send_message(phrase)

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
        aaa = randint(0, 100)
        # self.bot.send_message(self.chat_id, f"Активность {self.nn_session}")
        # self.bot.send_message(self.chat_id, f"Активность2 {self._get_nn_request_type_and_url(4)}")
        # my_data = json.dumps({'text': 'Привет'}, ensure_ascii=True)
        # print(my_data)
        # print(self._get_nn_request(self._get_nn_request_type_and_url(4), {'text': 'Привет'}))
        # self.bot.send_message(self.chat_id, f"Активность3 {self._get_nn_request()}")

        if aaa < 6:
            self.drink()
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

    def set_nn_session(self):
        self.nn_session = requests.Session()
        # a = self.nn_session.request()
        # a.text
        self.nn_session.auth = (my_secrets.NN_LOGIN, my_secrets.NN_PASSWORD)
        try:
            nn_answer = self.nn_session.get(f'http://{NN_IPADRESS}:{NN_PORT}{NN_COMMANDS[0][1]}')
            if DEBUG_MODE:
                self.send_message2(f'[DEBUG] Нейросеть общения доступна... __{nn_answer}__')
        except Exception as e:
            if DEBUG_MODE:
                self.send_message2(f'[DEBUG] Нейросеть недоступна: {e}')

    def _get_nn_request_type_and_url(self, something=0):
        cb_init_adr = f'http://{NN_IPADRESS}:{NN_PORT}'
        if type(something) == int:
            return [NN_COMMANDS[something][0], f'{cb_init_adr}{NN_COMMANDS[something][1]}']
        if type(something) == list:
            return [something[0], f'{cb_init_adr}{"/" if something[1][0] != "/" else ""}{something[1]}']
        else:
            raise TypeError(
                f'Укажите, либо число от 0 до {len(NN_COMMANDS) - 1}, либо list["Тип запроса","Адрес запроса" ]')

    def _get_nn_request(self, req, json={'text': ''}):
        try:
            answer = self.nn_session.request(method=req[0], url=req[1], json=json)
            return answer.json()
        except Exception as e:
            if DEBUG_MODE:
                self.send_message2(f'[DEBUG] Ошибка запроса: {e}')

    def get_answer_from_nn(self, input_text):
        req_type = self._get_nn_request_type_and_url(4)
        answer = self._get_nn_request(req_type, {"text": input_text})
        print(answer)
        return answer['text']


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
