from telebot import *
from Data import *


class Bot:
    #может находиться в двух состояниях - игра есть игры нет
    #делит пользователей на ведущего игры и ее участников
    game = False
    leader = ''
    leader_id = -1

    def __init__(self, token):
        #создаем бота и наше хранилище пользователей
        self.token = token
        self.bot = TeleBot(token)
        self.data = Data('players', 'subscribers')

        @self.bot.message_handler(commands=['start'])
        def start(message):
            #событие - присоединение нового пользователя к боту
            user_id = message.from_user.id
            self.bot.send_message(user_id, 'Привет, ' + message.from_user.first_name)
            self.data.add_sub(user_id)

    def run(self):
        @self.bot.message_handler(commands=['create'])
        def create_game(message):
            #событие - кто то начинает игру
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

            target = self.data.get_not_players()
            target.remove(message.from_user.id)
            self.broadcast_message(target, self.leader + ' начинает игру, хотите присоединиться?')

            instruction = open('load questions instruction')
            self.bot.send_photo(self.leader_id, photo=open('example.png', 'rb'))
            self.bot.send_message(self.leader_id, instruction.read())

        @self.bot.message_handler(commands=['join'])
        def join_game(message):
            #событие - кто то присоединился к уже существущей игре
            if message.from_user.id == self.leader_id:
                return

            if not self.game:
                self.bot.send_message(message.from_user.id,
                                      'Игру пока никто не начинал, может быть хотите стать ведущим?')
            else:
                self.bot.send_message(message.from_user.id, 'Вы в игре, скоро начнут появляться вопросы')
                self.data.add_player(message.from_user.id)

        self.bot.polling(none_stop=True, timeout=0)

    def broadcast_message(self, target, text):
        #рассылает сообщения всем id из массива target
        for i in target:
            self.bot.send_message(i, text)
