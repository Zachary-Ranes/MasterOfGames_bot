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
        game_state 0: game has not start (players can still join)
        game_state 1: setup_game is running (players cant hit join)
        game_state 2: setup_round -> setup_night is running 
        game_state 3: looking for night actions from players
        game_state 4: setup_round -> setup_day is running
        game_state 5: looking for day actions from players
        game_state 6: day round is over 
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

        self.ids_of_innocents = []
        self.ids_of_mafiosi = []
        self.id_of_detective = None
        self.id_of_doctor = None
        self.ids_of_alive_players = []
        
        self.number_of_alive_mafiosi = 0
        self.number_of_alive_innocents = 0

        self.role_completed_mafia = False
        self.role_completed_detective = False
        self.role_completed_doctor = False
        
        self.id_of_saved_player = None
        self.id_of_dead_man = None

        self.ids_of_mafia_targets = {}
        self.ids_of_lych_targets = {}

    #
    def list_usernames(self, excluded_ids, list_of_player_ids):
        output = ""
        for player_id in list_of_player_ids:
            if player_id not in excluded_ids:
                output += " @" + self.players_id_to_username[player_id]
        return output

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

    #
    def can_game_start(self, player_id):
        if self.game_state != 0:
            return False
        if player_id not in self.ids_of_players:
            return False
        self.number_of_players = len(self.ids_of_players)
        if self.number_of_players < self.MIN_PLAYERS:
            return False
        else:
            self.game_state = 1
            return True

    #Method is called once after all players have joined 
    def setup_game(self):
        self.number_of_alive_mafiosi = int(round(self.number_of_players/3))
        self.number_of_alive_innocents = self.number_of_players \
                                        - self.number_of_alive_mafiosi
        self.ids_of_alive_players = self.ids_of_players
        shuffle(self.ids_of_players)
        for i in range(self.number_of_alive_mafiosi):
            self.ids_of_mafiosi.append(self.ids_of_players[i])
        self.id_of_detective = self.ids_of_players[self.number_of_alive_mafiosi]
        self.id_of_doctor = self.ids_of_players[self.number_of_alive_mafiosi+1]
        for player_id in self.ids_of_players:
            if player_id not in self.ids_of_mafiosi:
                self.ids_of_innocents.append(player_id)       
        self.message_for_group = (
            "The game of Mafia has started! \nThere are "
            +str(self.number_of_alive_mafiosi) +" mafiosi in the game.", 
            None)
        for player_id in self.ids_of_innocents:
            self.message_for_players[player_id] = (
                "You are innocent\nYou win when all mafiosi have been lynched", 
                None)
        for player_id in self.ids_of_mafiosi:
            self.message_for_players[player_id] = (
                "You are part of the Mafia\nYou win when the mafia has kills "\
                "all the innocents\nThe other mafiosi are:"
                +self.list_usernames([player_id], self.ids_of_mafiosi), 
                None)
        self.message_for_players[self.id_of_detective] = (
            "You are the Detective, you work with the innocents\nYou win when "\
            "all the mafiosi have been lynched\nYou get to learn the role of "\
            "one play every night",
            None)
        self.message_for_players[self.id_of_doctor] = (
            "You are the Doctor, you work with the innocents\nYou win when all"\
            " the mafia have been lynched\nYou can choose a different player "\
            "each night to keep alive even if the mafia attacks them", 
            None)
        shuffle(self.ids_of_players)
        self.game_state = 2

    #Method is called after setup_game and at the start of each round 
    def setup_round(self):
        if self.game_state == 2:
            self.setup_night()
        if self.game_state == 4:
            self.setup_day()

    #Sets up for a night round, edits group and to player messages
    def setup_night(self):
        self.message_for_group = (
            "The night has started, the mafia are plotting to kill someone.",
            None)
        self.message_for_players = {}
        markup_mafia = types.InlineKeyboardMarkup()
        for i in range(len(self.ids_of_innocents)):
            player_id = self.ids_of_innocents[i]
            if player_id in self.ids_of_alive_players:
                player_id_index = str(i)
                if len(player_id_index) == 1:  
                    player_id_index = "0"+player_id_index
                markup_mafia.row(types.InlineKeyboardButton(
                    callback_data="kill"+player_id_index+str(self.game_key), 
                    text="@"+self.players_id_to_username[player_id]))
        markup_doctor = types.InlineKeyboardMarkup()
        for i in range(len(self.ids_of_players)):
            player_id = self.ids_of_players[i]
            if player_id in self.ids_of_alive_players \
            and player_id != self.id_of_saved_player:
                player_id_index = str(i)
                if len(player_id_index) == 1:  
                    player_id_index = "0"+player_id_index
                markup_doctor.row(types.InlineKeyboardButton(
                    callback_data="heal"+ player_id_index +str(self.game_key), 
                    text="@"+self.players_id_to_username[player_id]))
        markup_detective = types.InlineKeyboardMarkup()
        for i in range(len(self.ids_of_players)):
            player_id = self.ids_of_players[i]
            if player_id in self.ids_of_alive_players \
            and player_id != self.id_of_detective:
                player_id_index = str(i)
                if len(player_id_index) == 1:  
                    player_id_index = "0"+player_id_index
                markup_detective.row(types.InlineKeyboardButton(
                    callback_data="look"+ player_id_index +str(self.game_key), 
                    text="@"+self.players_id_to_username[player_id]))
        for player_id in self.ids_of_mafiosi:
            if player_id in self.ids_of_alive_players:
                self.message_for_players[player_id] = (
                    "Who do you want to kill? Once all the mafia wants to kill"\
                    " the same person that person will be killed", 
                    markup_mafia)
        if self.id_of_doctor in self.ids_of_alive_players:
            self.message_for_players[self.id_of_doctor] = (
                "Who do you want to heal tonight?", 
                markup_doctor)
        if self.id_of_detective in self.ids_of_alive_players:
            self.message_for_players[self.id_of_detective] = (
                "Who do you want to check the role of?", 
                markup_detective)
        self.role_completed_mafia = False
        self.role_completed_detective = False
        self.role_completed_doctor = False
        self.ids_of_mafia_targets = {}
        self.id_of_dead_man = None
        self.game_state = 3

    #
    def mafia_logic(self, mafia_id, id_of_player_voted_to_be_killed):
        if self.game_state != 3 \
        or id_of_player_voted_to_be_killed not in self.ids_of_alive_players\
        or mafia_id not in self.ids_of_alive_players\
        or mafia_id not in self.ids_of_mafiosi\
        or self.role_completed_mafia:
            return False
        self.ids_of_mafia_targets[mafia_id] = id_of_player_voted_to_be_killed
        markup_mafia = types.InlineKeyboardMarkup()
        for i in range(len(self.ids_of_innocents)):
            player_id = self.ids_of_innocents[i]
            if player_id in self.ids_of_alive_players:
                player_id_index = str(i)
                if len(player_id_index) == 1:  
                    player_id_index = "0" + player_id_index
                vote_count = 0
                for targeter_id in self.ids_of_mafia_targets: 
                    if self.ids_of_mafia_targets[targeter_id]==player_id:
                        vote_count = vote_count + 1
                markup_mafia.row(types.InlineKeyboardButton(
                    callback_data="kill"+ player_id_index +str(self.game_key), 
                    text="@"+self.players_id_to_username[player_id]+" "
                         +str(vote_count)))
                if vote_count == self.number_of_alive_mafiosi:
                    self.role_completed_mafia = True
                    self.id_of_dead_man = player_id 
        output = {}
        if self.role_completed_mafia:
            for player_id in self.ids_of_mafiosi:
                if player_id in self.ids_of_alive_players:
                    output[player_id] = (
                        "The mafia will be visiting @"
                        + self.players_id_to_username[self.id_of_dead_man]
                        +" tonight.",
                        None)
            return output
        else:
            for player_id in self.ids_of_mafiosi:
                if player_id in self.ids_of_alive_players:
                    output[player_id] = (
                        "Who do you want to kill? Once all the mafia wants to "\
                        "kill the same person that person will be killed", 
                        markup_mafia)
            return output

    #
    def doctor_logic(self, player_id, id_of_player_to_save):
        if self.game_state != 3 \
        or id_of_player_to_save not in self.ids_of_alive_players\
        or player_id not in self.ids_of_alive_players\
        or player_id != self.id_of_doctor\
        or self.role_completed_doctor:
            return False
        self.role_completed_doctor = True
        self.id_of_saved_player = id_of_player_to_save
        return ("@"+ self.players_id_to_username[id_of_player_to_save]
               +" will be saved saved if the mafia attack them tonight.",
                None)

    #
    def detective_logic(self, player_id, id_of_player_to_search):
        if self.game_state != 3 \
        or id_of_player_to_search not in self.ids_of_alive_players\
        or player_id not in self.ids_of_alive_players\
        or player_id != self.id_of_detective\
        or self.role_completed_detective:
            return False
        self.role_completed_detective = True
        if id_of_player_to_search in self.ids_of_innocents:
            if id_of_player_to_search == self.id_of_doctor:
                return ("@"+self.players_id_to_username[id_of_player_to_search] 
                       +" is the doctor.",
                        None)
            else:
                return ("@"+self.players_id_to_username[id_of_player_to_search]
                       +" is an innocent towns person.",
                        None)
        if id_of_player_to_search in self.ids_of_mafiosi:
            return ("@"+self.players_id_to_username[id_of_player_to_search] \
                   +" is part of the mafia.",
                    None)

    #
    def night_over(self):
        if self.id_of_doctor not in self.ids_of_alive_players:
            self.role_completed_doctor = True
        if self.id_of_detective not in self.ids_of_alive_players:
            self.role_completed_detective = True
        if (self.role_completed_mafia 
        and self.role_completed_detective
        and self.role_completed_doctor):
            if self.id_of_dead_man != self.id_of_saved_player:
                self.message_for_group = (
                    "During the night @"
                    +self.players_id_to_username[self.id_of_dead_man] 
                    +" was killed by the mafia",
                    None)       
                self.ids_of_alive_players.remove(self.id_of_dead_man)
                self.number_of_alive_innocents = \
                    self.number_of_alive_innocents - 1
            else:
                self.message_for_group = (
                    "During the night @" 
                    +self.players_id_to_username[self.id_of_dead_man] 
                    +" was attacked by the mafia, luckily the doctor also "\
                    "visited that night and saved a life",
                    None)
            self.message_for_players = {}
            self.game_state = 4
            return True
        else:
            return False

    #
    def setup_day(self):        
        markup_day = types.InlineKeyboardMarkup()
        for player_id in self.ids_of_players:
            if player_id in self.ids_of_alive_players:
                markup_day.row(types.InlineKeyboardButton(
                    callback_data="lynch"+ str(player_id), 
                    text="@"+self.players_id_to_username[player_id]))
        self.message_for_group = (
            "It is now the day, who should be lynched?\nIf half or more of "\
            "the players are voting for the same person they will be lynched",
            markup_day)
        self.message_for_players = {}
        self.ids_of_lych_targets = {}
        self.game_state = 5

    #
    def lynch_logic(self, voter_id, id_of_player_to_be_lyched):
        if self.game_state != 5\
        or id_of_player_to_be_lyched not in self.ids_of_alive_players\
        or voter_id not in self.ids_of_alive_players:
            return False
        self.ids_of_lych_targets[voter_id] = id_of_player_to_be_lyched
        markup_lynch = types.InlineKeyboardMarkup()
        for player_id in self.ids_of_alive_players:
            vote_count = 0
            for targeter_id in self.ids_of_lych_targets: 
                if self.ids_of_lych_targets[targeter_id]==player_id:
                    vote_count = vote_count + 1            
            markup_lynch.row(types.InlineKeyboardButton(
                callback_data="lynch"+str(player_id), 
                text="@"+self.players_id_to_username[player_id]+" "\
                     +str(vote_count)))
            if vote_count >= ((self.number_of_alive_mafiosi \
                              + self.number_of_alive_innocents)/2.0):
                self.ids_of_alive_players.remove(player_id)
                if player_id in self.ids_of_mafiosi:
                    self.number_of_alive_mafiosi = \
                        self.number_of_alive_mafiosi - 1
                if player_id in self.ids_of_innocents:
                    self.number_of_alive_innocents = \
                        self.number_of_alive_innocents - 1
                self.game_state = 6
                return ("@"+self.players_id_to_username[player_id]
                        +" has been lynched by the mob", 
                        None)
        return ("It is now the day, who should be lynched?\nIf half or more of"\
                " the players are voting for the same person they will be "\
                "lynched\n**The number next to someones name is the number of "\
                "votes to lynch them**",
                markup_lynch)

    #
    def day_over(self):
        if self.game_state != 6:
            return False
        else:
            self.message_for_players = {}
            self.message_for_group = (
                "The dark day is over, there are now " 
                + str(self.number_of_alive_mafiosi
                    +self.number_of_alive_innocents) 
                + " people left."
                ,None)
            self.game_state = 2
            return True

    #
    def end_state(self):
        if self.number_of_alive_innocents == 0:
            return "And with that all the innocent are dead\nthe Mafia Win!!!"
        if self.number_of_alive_mafiosi == 0:
            return "And the last mafia member dies\nTown's people Win!!!"
        else:
            return False


