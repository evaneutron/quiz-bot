from array import *


class Data:
    def __init__(self, players, subscribers):
        #инициализация хранилища - подгрузка всех пользователей с файлов
        self.subscribers_file_name = subscribers

        self.players = array('i')
        self.subscribers = array('i')

        subscribers_file = open(subscribers, 'r')

        for line in subscribers_file:
            line = line.rstrip('\n')
            if line != '':
                self.subscribers.append(int(line))

        subscribers_file.close()

    def add_sub(self, user_id):
        #добавление нового пользователя бота, сразу пишем в файл
        for el in self.subscribers:
            if el == user_id:
                return

        subscribers_file = open(self.subscribers_file_name, 'a')
        subscribers_file.write(str(user_id) + '\n')
        self.subscribers.append(user_id)

        subscribers_file.close()

    def add_player(self, user_id):
        #добавление нового участника игры
        for el in self.players:
            if el == user_id:
                return
        self.players.append(user_id)

    def get_not_players(self):
        #дает всех пользователей кто в данный момент не в игре, ведущий тоже будет в их числе
        not_players = array('i')
        for i in range(len(self.subscribers)):
            if i not in self.players:
                not_players.append(self.subscribers[i])

        return not_players

    def get_players(self):
        new_players = array('i')
        for i in self.players:
            new_players.append(i)

        return new_players

    def get_player_index(self, user_id):
        for i in range(len(self.players)):
            if self.players[i] == user_id:
                return i

    def players_contains(self, value):
        for i in self.players:
            if i == value:
                return True

        return False

    def clear_players(self):
        self.players = array('i')
