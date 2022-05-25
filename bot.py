from telebot import TeleBot
from data import Data
from telebot import types
from table import Table


class Bot:

    def __init__(self, token):
        self.bot = TeleBot(token)
        self.data = Data('source/players', 'source/subscribers.json')

        self.game = False
        self.load = False

        self.leader = None
        self.leader_id = -1
        self.players_cnt = 0

        self.questions = None
        self.questions_cnt = None

        self.curren_question = 0
        self.curren_answers_cnt = 0

        self.table = Table()

    def define_reactions(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            markup = self.create_main_menu()
            user_id = message.from_user.id
            self.bot.send_message(user_id, 'Привет, ' + message.from_user.first_name, reply_markup=markup)

            self.data.add_subscriber(user_id)

        @self.bot.message_handler(content_types=['text'])
        def get_text_message(message):
            message_text2action = {
                'Начать': self.start_game,
                'Присоединиться': self.join_game,
                'Опубликовать следующий вопрос': self.publish_next_question,
                'Закончить игру': self.end_game,
            }

            if message.text in message_text2action:
                message_text2action[message.text](message)

            elif self.is_num(message.text):
                self.handle_numeric_event(message)

        @self.bot.message_handler(content_types=['document'])
        def get_document(message):
            if self.game and not self.load and message.from_user.id != self.leader_id:
                self.load_questions(message)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button = types.KeyboardButton('Опубликовать следующий вопрос')
                markup.add(button)
                self.bot.send_message(self.leader_id, 'Нажмите на кнопку, чтобы опубликовать вопрос',
                                      reply_markup=markup)

        self.bot.polling(none_stop=True, timeout=0)

    def start_game(self, message):
        self.handle_player_start(message)
        self.handle_leader_start(message)

    def join_game(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if message.from_user.id == self.leader_id or self.data.players_contains(message.from_user.id):
            return

        if not self.game:
            self.bot.send_message(message.from_user.id,
                                  'Игру пока никто не начинал, может быть хотите стать ведущим?', reply_markup=markup)
        else:
            self.join_user()

    def broadcast_message(self, target, text, reply_markup):
        #рассылает сообщения всем id из массива target
        for i in target:
            self.bot.send_message(i, text, reply_markup=reply_markup)

    def send_instructions(self):
        self.bot.send_photo(self.leader_id, photo=open('source/example.png', 'rb'))
        self.bot.send_message(self.leader_id, 'Вопросы должны быть отделены одним отступом')

    def load_questions(self, message):
        file_name = self.bot.get_file(message.document.file_id)
        file = self.bot.download_file(file_name.file_path)
        str = file.decode()

        #mac
        #self.questions = str.split('\r\n\r\n')
        #windows
        self.questions = str.split('\n\n')
        self.questions_cnt = len(self.questions)

        try:
            self.table.fill_questions(self.questions_cnt)
        except Exception:
            print("Google table error")

    def send_question(self):
        question = self.questions[self.curren_question]
        answers = question.split('\n')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for i in range(len(answers) - 1):
            button = types.KeyboardButton(str(i + 1))
            markup.add(button)

        self.broadcast_message(self.data.get_players_copy(), question, reply_markup=markup)
        self.curren_answers_cnt = len(answers) - 1
        self.curren_question += 1

    def create_main_menu(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Начать')
        button2 = types.KeyboardButton('Присоединиться')
        markup.add(button1, button2)
        return markup

    def end_game(self, message):
        markup = self.create_main_menu()

        players = self.data.get_players_copy()
        players.append(self.leader_id)

        self.broadcast_message(players,
                              'Игра окончена. Результаты будут выгружены в таблицу', reply_markup=markup)

        self.set_default_fields()

    def set_default_fields(self):
        self.game = False
        self.load = False
        self.leader = None
        self.leader_id = -1
        self.players_cnt = 0
        self.questions = None
        self.data.clear_players()
        self.questions_cnt = None
        self.curren_question = 0
        self.curren_answers_cnt = 0

    def publish_next_question(self, message):
        if self.curren_question == self.questions_cnt - 1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button = types.KeyboardButton('Закончить игру')
            markup.add(button)
            self.bot.send_message(self.leader_id, 'Закончу игру по вашей команде', reply_markup=markup)

        self.send_question()

    def handle_player_start(self, message):
        if self.game and message.from_user.id != self.leader_id:
            self.bot.send_message(message.from_user.id,
                                  self.leader + ' уже начинает игру, вы хотите присоединиться' +
                                  message.from_user.first_name)

    def handle_leader_start(self, message):
        self.leader = message.from_user.first_name
        self.leader_id = message.from_user.id

        self.bot.send_message(message.from_user.id, 'Вы начали игру')
        self.game = True

        markup = self.create_main_menu()
        not_players = self.data.get_not_players()
        not_players.remove(message.from_user.id)

        self.broadcast_message(not_players, self.leader + ' начинает игру, хотите присоединиться?', reply_markup=markup)
        self.send_instructions()

    def handle_numeric_event(self, message):
        answer_num = int(message.text)
        name = message.from_user.first_name

        if answer_num > self.curren_answers_cnt or answer_num < 1:
            self.bot.send_message(message.from_user.id, "Ответа с таким номером нет")
        else:
            self.bot.send_message(self.leader_id, name +
                                  " Отвечает на " + str(self.curren_question) + " Вопрос")

        index = self.data.get_player_index(message.from_user.id)

        try:
            self.table.add_answer(answer_num, index, self.curren_question)
        except Exception:
            print("Google table error")

    def join_user(self):
        self.bot.send_message(message.from_user.id, 'Вы в игре, скоро начнут появляться вопросы',
                              reply_markup=markup)
        self.data.add_player(message.from_user.id)
        self.players_cnt += 1

        players = self.data.get_players_copy()
        players.append(self.leader_id)

        self.bot.send_message(self.leader_id, message.from_user.first_name + ' присоединяется', reply_markup=None)

        index = self.data.get_player_index(message.from_user.id)

        try:
            self.table.add_user(message.from_user.first_name, index)
        except Exception:
            print("Google table error")


def is_num(self, string):
    try:
        int(string)
    except ValueError:
        return False

    return True