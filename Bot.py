from telebot import *
from Data import *
from telebot import types
import table


class Bot:
    #todo end game
    #может находиться в двух состояниях - игра есть игры нет
    #делит пользователей на ведущего игры и ее участников
    game = False
    load = False

    leader = None
    leader_id = -1
    players_cnt = 0

    questions = None
    questions_cnt = None

    curren_question = 0
    curren_answers_cnt = 0

    def __init__(self, token):
        #создаем бота и наше хранилище пользователей
        self.token = token
        self.bot = TeleBot(token)
        self.data = Data('source/players', 'source/subscribers')

    def define_reactions(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            # событие - присоединение нового пользователя к боту
            markup = self.create_main_menu()
            user_id = message.from_user.id
            self.bot.send_message(user_id, 'Привет, ' + message.from_user.first_name, reply_markup=markup)

            self.data.add_sub(user_id)

        @self.bot.message_handler(content_types=['text'])
        def get_text_message(message):
            if message.text == 'Начать':
                self.start_game(message)

            elif message.text == 'Присоединиться':
                self.join_game(message)

            elif message.text == 'Опубликовать следующий вопрос':
                if self.curren_question == self.questions_cnt - 1:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    button = types.KeyboardButton('Закончить игру')
                    markup.add(button)
                    self.bot.send_message(self.leader_id, 'Закончу игру по вашей команде', reply_markup=markup)

                self.send_question()

            elif message.text == 'Закончить игру':
                self.end_game()

            elif self.is_num(message.text):
                answer_num = int(message.text)
                name = message.from_user.first_name

                if answer_num > self.curren_answers_cnt or answer_num < 1:
                    self.bot.send_message(message.from_user.id, "Ответа с таким номером нет")
                else:
                    self.bot.send_message(self.leader_id, name +
                                          " Отвечает на " + str(self.curren_question) + " Вопрос")

                index = self.data.get_player_index(message.from_user.id)

                try:
                    table.add_answer(answer_num, index, self.curren_question)
                except Exception:
                    print("Google table error")

        @self.bot.message_handler(content_types=['document'])
        def get_document(message):
            if self.game:
                if message.from_user.id != self.leader_id:
                    return
                elif self.load:
                    return
                else:
                    self.load_questions(message)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    button = types.KeyboardButton('Опубликовать следующий вопрос')
                    markup.add(button)
                    self.bot.send_message(self.leader_id, 'Нажмите на кнопку, чтобы опубликовать вопрос',
                                          reply_markup=markup)

        self.bot.polling(none_stop=True, timeout=0)

    def start_game(self, message):
        # событие - кто то начинает игру
        if self.game:
            if message.from_user.id == self.leader_id:
                return

            self.bot.send_message(message.from_user.id,
                                  self.leader + ' уже начинает игру, вы хотите присоединиться' +
                                  message.from_user.first_name)
            return

        self.leader = message.from_user.first_name
        self.leader_id = message.from_user.id

        self.bot.send_message(message.from_user.id, 'Вы начали игру')
        self.game = True

        markup = self.create_main_menu()

        not_players = self.data.get_not_players()
        not_players.remove(message.from_user.id)
        self.broadcast_message(not_players, self.leader + ' начинает игру, хотите присоединиться?', reply_markup=markup)

        self.send_instructions()

    def join_game(self, message):
        # событие - кто то присоединился к уже существущей игре
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if message.from_user.id == self.leader_id:
            return

        if self.data.players_contains(message.from_user.id):
            return

        if not self.game:
            self.bot.send_message(message.from_user.id,
                                  'Игру пока никто не начинал, может быть хотите стать ведущим?', reply_markup=markup)
        else:
            self.bot.send_message(message.from_user.id, 'Вы в игре, скоро начнут появляться вопросы',
                                  reply_markup=markup)
            self.data.add_player(message.from_user.id)
            self.players_cnt += 1

            players = self.data.get_players()
            players.append(self.leader_id)

            self.bot.send_message(self.leader_id, message.from_user.first_name + ' присоединяется', reply_markup=None)

            index = self.data.get_player_index(message.from_user.id)

            try:
                table.add_user(message.from_user.first_name, index)
            except Exception:
                print("Google table error")


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
        self.questions = str.split('\r\n\r\n')
        #windows
        #self.questions = str.split('\n\n')
        self.questions_cnt = len(self.questions)

        try:
            table.fill_questions(self.questions_cnt)
        except Exception:
            print("Google table error")

    def send_question(self):
        question = self.questions[self.curren_question]
        #in answers also there is topic
        answers = question.split('\n')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for i in range(len(answers) - 1):
            button = types.KeyboardButton(str(i + 1))
            markup.add(button)

        self.broadcast_message(self.data.get_players(), question, reply_markup=markup)
        self.curren_answers_cnt = len(answers) - 1
        self.curren_question += 1

    def create_main_menu(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Начать')
        button2 = types.KeyboardButton('Присоединиться')
        markup.add(button1, button2)
        return markup

    def end_game(self):
        markup = self.create_main_menu()

        players = self.data.get_players()
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

    def is_num(self, str):
        try:
            int(str)
        except ValueError:
            return False

        return True
