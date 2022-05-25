from array import array
import json
from copy import copy

class Data:
    def __init__(self, players, subscribers):
        self.subscribers_file_name = subscribers

        self.players = array('i')

        self.subscribers = array('i')

        with open(subscribers, 'r') as subscribers_file:
            self.subscribers = json.load(subscribers_file)['subscribers']

        subscribers_file.close()

    def add_subscriber(self, user_id):
        if user_id in self.subscribers:
            return

        self.subscribers.append(user_id)

    def add_player(self, user_id):
        if user_id in self.players:
            return

        self.players.append(user_id)

    def get_not_players(self):
        not_players = array('i')
        for i in range(len(self.subscribers)):
            if i not in self.players:
                not_players.append(self.subscribers[i])

        return not_players

    def get_players_copy(self):
        return copy(self.players)

    def get_player_index(self, user_id):
        try:
            return self.players.index(user_id)
        except ValueError:
            return None

    def players_contains(self, value):
        return value in self.players

    def clear_players(self):
        self.players = array('i')

    def __del__(self):
        obj = {'subscribers': self.subscribers}
        print("123")

        with open(self.subscribers_file_name, 'w') as subscribers_file:
            json.dump(obj, subscribers_file)
