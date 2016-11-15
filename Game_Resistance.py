#Author: Zachary Ranes
#Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

import math
from random import shuffle
import telebot
from telebot import types

#
class Resistance():
    #Constructor for class 
    def __init__(self, key):
        self.game_name = "resistance"
        self.game_key = key
        self.game_state = 0
        """
        game_state is set to 0 in the parent class construct
        game_state = 0 : game has not start (players can still join)
        game_state = 1 : the game has started (players cant hit join)
        game_state = 2 : looking for nominees for a mission
        game_state = 3 : looking for votes on nominees for mission
        game_state = 4 : voting over, players going on mission
        game_state = 5 : mission over next round is being set up or game is over
        """
        self.MIN_PLAYERS = 5
        self.MAX_PLAYERS = 10
        self.number_of_players = 0
        self.ids_of_players = []
        self.players_id_to_username = {}
        self.players_username_to_id = {}

        self.message_for_group = None
        self.message_for_players = {}
        self.last_messages_ids = {}

        #The 3d array here will find the nominees that will be need per round 
        self.FIVE_PLAYERS = [2,3,2,3,3]
        self.SIX_PLAYERS = [2,3,4,3,4]
        self.SEVEN_PLAYERS = [2,3,3,4,4]
        self.EIGHT_PLUS_PLAYERS = [3,4,4,5,5]
        self.PLAYERS_PER_ROUND = [self.FIVE_PLAYERS, 
                                  self.SIX_PLAYERS, 
                                  self.SEVEN_PLAYERS, 
                                  self.EIGHT_PLUS_PLAYERS, 
                                  self.EIGHT_PLUS_PLAYERS, 
                                  self.EIGHT_PLUS_PLAYERS]

        self.game_round = 0
                
        self.ids_of_resistances = []
        self.ids_of_spies = []
        self.number_of_spies = 0
        
        self.id_of_nominator = None
        self.last_nominator_index = 0
        
        self.number_of_nominees = None
        self.two_fail_mission = False
        
        self.ids_of_players_going_on_mission = []

        self.ids_of_players_voted_on_nominees = []
        self.nominees_yea_votes = 0
        self.nominees_nay_votes = 0
        
        self.ids_of_players_voted_from_mission = []
        self.mission_fail_votes = 0
        self.mission_pass_votes = 0
        
        self.points_spies = 0
        self.points_resistance = 0
    
    #
    def list_usernames(self, excluded_id, list_of_player_ids):
        output = ""
        for player_id in list_of_player_ids:
            if player_id != excluded_id:
                output += " @" + self.players_id_to_username[player_id]
        return output

    #Returns a tubal of message and markup
    def setup_pregame(self):
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="MoG_join",
                                              text="Join"))
        return ("You have selected the game resistance.\n"\
                "To play resistance we need 5 to 10 players.",
                markup)

    #
    def add_player(self, player_id, player_username, player_name):
        if (self.game_state != 0 
        or player_id in self.ids_of_players
        or len(self.ids_of_players) >= self.MAX_PLAYERS):
            return False
        message_text = "Resistance needs 5 to 10 players"
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
        self.number_of_spies = int(math.ceil(self.number_of_players/3))
        #shuffling user IDs so the roles are not determined by join order
        shuffle(self.ids_of_players)
        for spy_index in range(self.number_of_spies):
            self.ids_of_spies.append(self.ids_of_players[spy_index])
        for player_id in self.ids_of_players:
            if player_id not in self.ids_of_spies:
                self.ids_of_resistances.append(player_id)
        self.message_for_group = ("This game of resistance has "
                                  + str(self.number_of_spies) +" spies in it",
                                  None)
        for player_id in self.ids_of_resistances:
            self.message_for_players[player_id] = (
                "You are part of the Resistance\nYou win when 3 missions "\
                "succeed", None)
        for player_id in self.ids_of_spies:
            self.message_for_players[player_id] = (
                "You are a Spy\nYou win when 3 missions fail\nThe other spies "\
                "are:"+self.list_usernames(player_id, self.ids_of_spies), None)
        #shuffled again so turn order does not give away roles
        shuffle(self.ids_of_players)

    #Method called at the start of every round of the game
    def setup_round(self):
        self.id_of_nominator = self.ids_of_players[self.last_nominator_index]   
        self.last_nominator_index += 1
        if self.last_nominator_index == self.number_of_players:
            self.last_nominator_index == 0
        #Game rule certain mission will need two fail votes to fail 
        if self.game_round == 3 and self.number_of_players >= 7:
            self.two_fail_mission = True
            extra_message = "This round requires two spies "\
                            "to vote for failure to fail"
        else:
            self.two_fail_mission = False
            extra_message = ""
        self.number_of_nominees = \
            self.PLAYERS_PER_ROUND[self.number_of_players-self.MIN_PLAYERS]\
                                  [self.game_round]
        self.message_for_group = \
            ("@"+ self.players_id_to_username[self.id_of_nominator] +" gets to"\
            " nominate "+ str(self.number_of_nominees) +" players to go on the"\
            " mission. "+ extra_message +"\nNominate players by typing "\
            "/nominate (space) @username (space) @username ...etc", None)
        self.message_for_players = {}
        self.game_state = 2

    #
    def nominate_logic(self, player_id, entities, text):
        if self.game_state != 2: 
            return ("It is not the time to run that command",None) 
        if player_id != self.id_of_nominator:
            return ("You are not the nominator right now",None)
        self.ids_of_players_going_on_mission = []
        mentioned = []
        for i in range(len(entities)):
            if entities[i].type == "mention":
                starting_index = entities[i].offset +1
                ending_index = entities[i].offset + entities[i].length
                username_without_at = text[starting_index:ending_index]
                mentioned.append(username_without_at)
        if len(mentioned) != self.number_of_nominees:
            return (("You nominated the wrong number of players.\nYou need to "\
                     " nominate "+ str(self.number_of_nominees) +" players all"\
                     " in the same message."), None)
        for i in range(len(mentioned)):
            username = mentioned[i]
            if username not in self.players_username_to_id:
                return ("You nominated someone not playing", None)
            if self.players_username_to_id[username] in \
                                        self.ids_of_players_going_on_mission:
                return ("You nominated someone more than once", None)
            else:
                self.ids_of_players_going_on_mission.append(
                                        self.players_username_to_id[username])
        self.ids_of_players_voted_on_nominees = []
        self.nominees_yea_votes = 0
        self.nominees_nay_votes = 0
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(
                                        callback_data="MasterOfGames_bot_yea", 
                                        text="Yea"), 
                   types.InlineKeyboardButton(
                                        callback_data="MasterOfGames_bot_nay", 
                                        text="Nay"))
        self.game_state = 3
        return ("Now everyone vote on the proposed mission party.\nIf half or "\
                " more of the vote are nay the next player will get to "\
                "nominate players to go on a mission", markup)

    #If invalid input or game_staet returns false else returns update on 
    #nomination voting, changes game state if enough votes have been cast
    def nomination_vote_logic(self, player_id, vote):
        if (self.game_state != 3
        or player_id not in self.ids_of_players 
        or player_id in self.ids_of_players_voted_on_nominees):
            return False
        self.ids_of_players_voted_on_nominees.append(player_id)
        if vote == "yea":
            self.nominees_yea_votes += 1
            if self.nominees_yea_votes > self.number_of_players/2:
                self.game_state = 4
                self.message_for_group=("Enough yea votes have been cast, "\
                                        "the mission will take place.",None)
        if vote == "nay":
            self.nominees_nay_votes += 1
            if self.nominees_nay_votes >= self.number_of_players/2:
                self.game_state = 2
                self.message_for_group=("Enough nay votes have been cast, "\
                                        "the next player will get to nominate "\
                                        "someone now.",None)
        return "\n@"+self.players_id_to_username[player_id] +" has voted "+ vote
   
    #
    def setup_mission(self):
        self.mission_pass_votes = 0
        self.mission_fail_votes = 0
        self.ids_of_players_voted_from_mission = []
        self.message_for_group = (self.list_usernames(None, \
                                    self.ids_of_players_going_on_mission) 
                                 +" are now going on a mission", 
                                 None)
        markup_resistance = types.InlineKeyboardMarkup()
        markup_resistance.row(types.InlineKeyboardButton(
                                        callback_data="pass"+str(self.game_key), 
                                        text="Pass"))
        markup_spies = types.InlineKeyboardMarkup()
        markup_spies.row(types.InlineKeyboardButton(
                                        callback_data="pass"+str(self.game_key), 
                                        text="Pass"), 
                        types.InlineKeyboardButton(
                                        callback_data="fail"+str(self.game_key), 
                                        text="Fail"))
        self.message_for_players = {}
        for player_id in self.ids_of_players_going_on_mission:
            if player_id in self.ids_of_resistances:
                self.message_for_players[player_id] = (
                    "You are on a mission with"
                    +self.list_usernames(player_id, \
                        self.ids_of_players_going_on_mission), 
                    markup_resistance)
            if player_id in self.ids_of_spies:
                self.message_for_players[player_id] = (
                    "You are on a mission with"
                    +self.list_usernames(player_id, \
                        self.ids_of_players_going_on_mission), 
                    markup_spies)

    #
    def mission_logic(self, player_id, vote):
        if (self.game_state != 4 
        or player_id not in self.ids_of_players_going_on_mission 
        or player_id in self.ids_of_players_voted_from_mission):
            return False
        if vote == "pass":
            self.mission_pass_votes += 1   
        if vote == "fail" and player_id in self.ids_of_spies:
            self.mission_fail_votes += 1
        self.ids_of_players_voted_from_mission.append(player_id)

        if len(self.ids_of_players_going_on_mission) == \
                len(self.ids_of_players_voted_from_mission):
            if (self.mission_fail_votes >= 1 and not self.two_fail_mission 
            or self.mission_fail_votes >= 2 and self.two_fail_mission):
                self.points_spies += 1
                self.message_for_group = ("Mission failure!!!!!\n")                         
            else:
                self.points_resistance += 1
                self.message_for_group =  ("Mission success!!!!\n")
            self.game_round += 1
            self.message_for_group += ("The score is now:\n "
                                          +str(self.points_resistance) 
                                          +" for the Resistance \n"
                                          +str(self.points_spies)
                                          +" for the Spies")
            self.game_state = 5
        return self.message_for_players[player_id][0] +"\nYou voted: " + vote

    #
    def end_state(self):
        if self.points_resistance >= 3:
            return "The resistance has scored 3 points!!!\nThe resistance has "\
            " won the game, they have brought down the evil empire."
        if self.points_spies >= 3:
            return "The spies have scored 3 points!!!\nThe spies have won the "\
            "game, they have foiled the plot of the anti-government group."
        else:
            return False

