#Author: Zachary Ranes
#Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

import math
from random import shuffle
import telebot
from telebot import types

class Mafia():
    #Constructor for class 
    def __init__(self, key):
        self.game_name = "mafia"
        self.game_key = key
        self.game_state = 0
        """
        """
        self.MIN_PLAYERS = 7
        self.MAX_PLAYERS = 24
        self.number_of_players = 0
        self.ids_of_players = []
        self.players_id_to_username = {}
        self.players_username_to_id = {}

        self.message_for_group = None
        self.message_for_players = {}
        self.last_messages_ids = {}





    #Returns a tubal of message and markup
    def setup_pregame(self):
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="MoG_join",
                                              text="Join"))
        return ("You have selected the game mafia.\n"\
                "To play resistance we need 7 to 24 players.",
                markup)
    #
    def add_player(self, player_id, player_username, player_name):
        if (self.game_state != 0 
        or player_id in self.ids_of_players
        or len(self.ids_of_players) >= self.MAX_PLAYERS):
            return False
        message_text = "Mafia needs 7 to 24 players"
        extra_message = ""
        if player_username == None:
            extra_message = "\n*** "+ player_name +" you need an "\
                                                        "@UserName to play ***"
        else: 
            self.ids_of_players.append(player_id)
            self.players_id_to_username[player_id] = player_username
            self.players_username_to_id[player_username] = player_id
        for player_id in self.players_id_to_username:
            message_text += \
                    "\n@"+ self.players_id_to_username[player_id] +" is playing"
        markup = types.InlineKeyboardMarkup()
        if len(self.ids_of_players) < self.MAX_PLAYERS:
            markup.row(types.InlineKeyboardButton(callback_data="MoG_join",
                                                  text="Join"))
        if len(self.ids_of_players) >= self.MIN_PLAYERS:
            markup.row(types.InlineKeyboardButton(callback_data="MoG_start",
                                                  text="Start"))
        return (message_text+extra_message, markup)



