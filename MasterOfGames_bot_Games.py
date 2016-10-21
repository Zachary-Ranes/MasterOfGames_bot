#Author: Zachary Ranes
#Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

import telebot
from telebot import types
import math
from random import shuffle


class Game(object):
    
    #
    def __init__(self, game_code = None, min_players = None, max_players = None):
        #
        self.game_code = game_code
        
        #
        self.MIN_PLAYERS = min_players
        self.MAX_PLAYERS = max_players
        
        #
        self.game_state = 0
        self.game_state_before_pause = None
        
        #
        self.ids_of_players = []
        self.number_of_players = 0
        
        #
        self.players_id_to_username = {}
        self.players_username_to_id = {}
        
        #
        self.message_for_group = []
        self.message_for_players = {}
        self.last_messages = {}
    
        
    #takes a telegram users chat ID,  username and first name
    #returns a message if success or there can be no more players or returns None if a message should not be sent
    def add_player(self, player_id, player_username, player_name):
        if player_username == None:
            return "I am sorry "+ player_name +" but you must have an @UserName to play"
        
        if len(self.ids_of_players) == self.MAX_PLAYERS:
            return "I am sorry @"+ player_username +" but we already have the max number of player for this game"
       
        else: 
            self.ids_of_players.append(player_id)
            self.players_id_to_username[player_id] = player_username
            self.players_username_to_id[player_username] = player_id
            return "@"+ player_username +" has joined the game"
    
    
    #
    def enough_players(self):
        self.number_of_players = len(self.ids_of_players)
        
        if self.number_of_players < self.MIN_PLAYERS:
            self.message_for_group[0] = ("Not enough players have joined to start the game \nYou need "+str(self.MIN_PLAYERS)
                      +" to "+str(self.MAX_PLAYERS)+" people to play, "+str(self.number_of_players) +" players have joined")
        else:
            self.game_state = 1
        
        
    #
    def setup_game(self):
        pass
        
        
    #
    def setup_round(self):
        pass
              

    #
    def check_for_winner(self):
        pass
            
    #
    def pause_game(self, value):
        if value == True:
            self.game_state_before_pause = self.game_state
            self.game_state = -1
        if value == False:
            self.game_state = self.game_state_before_pause
            self.game_state_before_pause = None
            
        
    #
    def list_usernames(self, list_of_excluded_id, list_of_player_ids):
        output = ""
        for player_id in list_of_player_ids:
            if player_id not in list_of_excluded_id:
                output += " @" + self.players_id_to_username[player_id]
        return output
    
        
        
class Resistance(Game):

    def __init__(self, game_code = 1, min_players = 5, max_players = 10):
        super(Resistance, self).__init__(game_code, min_players, max_players)
   
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), 
                   types.InlineKeyboardButton(callback_data="start", text="Start Game"))
   
        self.message_for_group = ["You have selected the game resistance\nTo play resistance we need 5 to 10 people", markup]
   
        #This 2d array is the number of player in the game vs the number of player what will be needed for each round of the game 
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
        
        """
        game_state is set to 0 in the parent class constructor
        
        game_state = 0 : game has not start (players can still join)
        game_state = 1 : the game has started (players cant hit join)
        game_state = 2 : looking for nominees for a mission
        game_state = 3 : looking for votes on nominees for mission
        game_state = 4 : voting over, players going on mission
        game_state = -2 : game has ending one team has scored 3 points
        game_state = -1 = game is paused (waiting for the game to be ended or continued)
        """
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
        self.mission_yea_votes = 0
        self.mission_nay_votes = 0
        
        self.ids_of_players_voted_from_mission = []
        self.mission_fail_votes = 0
        self.mission_pass_votes = 0
        
        self.points_spies = 0
        self.points_resistance = 0

    
    #uses internal var 
    #returns nothing
    def setup_game(self):
        self.number_of_spies = int(math.ceil(self.number_of_players/3))
        #shuffling user IDs so the roles are not determined by what order people joined the game
        shuffle(self.ids_of_players)

        for i in range(self.number_of_spies):
            self.ids_of_spies.append(self.ids_of_players[i])
        
        for player_id in self.ids_of_players:
            if player_id not in self.ids_of_spies:
                self.ids_of_resistances.append(player_id)
                
        self.message_for_group[0] = "The game of Resistance has started! \nThere are "+ str(self.number_of_spies) +" spies in the game."
        self.message_for_group[1] = None
        
        for player_id in self.ids_of_resistances:
            self.message_for_players[player_id] = ("You are part of the Resistance\nYou win when 3 missions succeed", None)
            
        for player_id in self.ids_of_spies:
            self.message_for_players[player_id] = ("You are a Spy\n You win when 3 missions fail\nThe other spies are:" + self.list_usernames([player_id], self.ids_of_spies), None)

        #shuffled again so turn order does not give away roles
        shuffle(self.ids_of_players)
        self.game_state = 2

 
    #takes self
    #return message who gets to nominate and if there are special rules this round
    def setup_round(self):
        self.id_of_nominator = self.ids_of_players[self.last_nominator_index]   
         
        self.last_nominator_index += 1
        
        if self.last_nominator_index == self.number_of_players:
            self.last_nominator_index == 0
        

        #This if else is for the rule that some missions in the game will need two fail votes to fail
        if self.game_round == 3 and self.number_of_players >= 7:
            self.two_fail_mission = True
            extra_message = "This round requires two spies to vote for failure to fail\n"
        else:
            self.two_fail_mission = False
            extra_message = ""

        self.number_of_nominees = self.PLAYERS_PER_ROUND[self.number_of_players-self.MIN_PLAYERS][self.game_round]
        self.message_for_group[0] = ("@"+ self.players_id_to_username[self.id_of_nominator] 
                                 +" gets to nominate "+ str(self.number_of_nominees) 
                                 +" players to go on the mission\n"+ extra_message
                                 +"Nominate players by typing /nominate (space) @username (space) @username ...etc")
        self.message_for_group[1] = None
        self.message_for_players = {}
    
    
    #takes self
    #changes games state to 5 and changes group message if there is a winner
    def check_for_winner(self):
        if self.points_resistance == 3:
            self.game_state = -2
            self.message_for_group[0] = "The resistance has scored 3 points!!!\nThe resistance has won the game"
            
        if self.points_spies == 3:
            self.game_state = -2
            self.message_for_group[0] = "The spies have scored 3 points!!!\nThe spies have won the game"

               
    #takes self an array of telegram chat entities and a chat messages text
    #returns message about whether the message was a valid nomination
    def nominate_logic(self, entities, text):
        mentioned = []
        self.ids_of_players_going_on_mission = []
        for i in range(len(entities)):
            if entities[i].type == "mention":
                starting_index = entities[i].offset +1
                ending_index = entities[i].offset + entities[i].length
                username_without_at = text[starting_index:ending_index]
                mentioned.append(username_without_at)

        if len(mentioned) != self.number_of_nominees:
            self.message_for_group[0] = ("You nominated the wrong number of players\nYou need to nominate "+ str(self.number_of_nominees) 
                                        +" players \nDo this by typing /nominate then the username of the players you want to nominate all in the same message")
            self.message_for_group[1] = None
            return

        for i in range(len(mentioned)):
            if mentioned[i] not in self.players_username_to_id:
                self.message_for_group[0] = "You nominated someone not playing"
                self.message_for_group[1] = None
                return
                
            if self.players_username_to_id[mentioned[i]] in self.ids_of_players_going_on_mission:
                self.message_for_group[0] = "You nominated someone more than once"
                self.message_for_group[1] = None
                return
                
            else:
                self.ids_of_players_going_on_mission.append(self.players_username_to_id[mentioned[i]])

        self.ids_of_players_voted_on_nominees = []
        self.mission_yea_votes = 0
        self.mission_nay_votes = 0
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="yea", text="Yea"), 
                   types.InlineKeyboardButton(callback_data="nay", text="Nay"))
        
        self.message_for_group[0] = "Now everyone vote on the proposed mission party\nIf half or more of the vote are nay the next player will get to nominate"
        self.message_for_group[1] = markup
        
        self.game_state = 3
        return


    #takes self, telegram user id and callback data (a string)
    #does calculation, returns message if votes changes state
    def vote_logic(self, player_id, vote):
        if vote == "yea":
            self.mission_yea_votes += 1
            if self.mission_yea_votes > self.number_of_players/2:
                self.game_state = 4

        if vote == "nay":
            self.mission_nay_votes += 1
            if self.mission_nay_votes >= self.number_of_players/2:
                self.game_state = 2

        self.ids_of_players_voted_on_nominees.append(player_id)
        return "@"+ self.players_id_to_username[player_id] +" has voted "+ vote
        
  
    #takes self
    #setup for var for a mission 
    def setup_mission(self, key):
        self.mission_pass_votes = 0
        self.mission_fail_votes = 0
        self.ids_of_players_voted_from_mission = []

        self.message_for_group[0] = "Enough yea votes have been cast,"+ self.list_usernames(None, self.ids_of_players_going_on_mission) +" are now going on a mission"
        self.message_for_group[1] = None
        
        #these two markups add the group chats Id (key) to there callback data so the callback can be associated to the group chat
        markup_resistance = types.InlineKeyboardMarkup()
        markup_resistance.row(types.InlineKeyboardButton(callback_data="pass"+str(key), text="Pass"))
        
        markup_spies = types.InlineKeyboardMarkup()
        markup_spies.row(types.InlineKeyboardButton(callback_data="pass"+str(key), text="Pass"), 
                        types.InlineKeyboardButton(callback_data="fail"+str(key), text="Fail"))
             
        self.message_for_players = {}

        for player_id in self.ids_of_players_going_on_mission:
            if player_id in self.ids_of_resistances:
                self.message_for_players[player_id] = ("You are on a mission with" + self.list_usernames([player_id], self.ids_of_players_going_on_mission), markup_resistance)
            if player_id in self.ids_of_spies:
                self.message_for_players[player_id] = ("You are on a mission with" + self.list_usernames([player_id], self.ids_of_players_going_on_mission), markup_spies)
                
    
    #takes self, players id and string that is there vote on whether the mission passes or not
    #changes games state to 2 if the voting round is over or to state 5 if that was the last round
    #returns two outputs the first being a message if a mission failed or not and the second being a message about the game ending
    def mission_logic(self, player_id, vote):
        if vote == "pass":
            self.mission_pass_votes += 1
        
        if vote == "fail" and player_id in self.ids_of_spies:
            self.mission_fail_votes += 1
        
        self.ids_of_players_voted_from_mission.append(player_id)

        if len(self.ids_of_players_going_on_mission) == len(self.ids_of_players_voted_from_mission):
           
            if (self.mission_fail_votes >= 1 and self.two_fail_mission == False 
             or self.mission_fail_votes >= 2 and self.two_fail_mission == True):
                self.points_spies += 1
                self.message_for_group[0] = ("Mission fails !!!!!\n") 
                         
            else:
                self.points_resistance += 1
                self.message_for_group[0] =  ("Mission passed!!!! \n")

            self.game_round += 1
            self.message_for_group[0] += ("The score is now:\n "
                                            + str(self.points_resistance) +" for the Resistance \n"
                                            + str(self.points_spies) +" for the Spies")
            self.game_state = 2



class Mafia(Game):
    
    #
    def __init__(self, game_code = 2, min_players = 7, max_players = 24):
        super(Mafia, self).__init__(game_code, min_players, max_players)

        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), 
                   types.InlineKeyboardButton(callback_data="start", text="Start Game"))

        self.message_for_group = ["You have selected the game mafia\nTo play mafia we need 7 to 21 people", markup]
        
        """
        game_state is set to 0 in the parent class constructor
        
        game_state = 0 : game has not start (players can still join)
        game_state = 1 : the game has started (players cant hit join)
        game_state = 2 : night time waiting for all night actors to vote
        game_state = 3 : day time looking for nominees to lynch
        game_state = 4 : day time, voting on who to lynch

        game_state - -2 : game is over about to be deleted 
        game_state = -1 : game is paused (waiting for the game to be ended or continued)
        """

        self.ids_of_innocents = []
        self.ids_of_mafiosi = []
        self.number_of_mafiosi = 0
        self.role_completed_mafia = False
        self.ids_of_mafia_targets = {}

        self.id_of_detective = None
        self.role_completed_detective = False

        self.id_of_doctor = None
        self.role_completed_doctor = False
        self.id_of_saved_player = None


    #
    def setup_game(self):
        self.number_of_mafiosi = int(round(self.number_of_players/3))

        shuffle(self.ids_of_players)
        
        for i in range(self.number_of_mafiosi):
            self.number_of_mafiosi.append(self.ids_of_players[i])
        
        self.id_of_detective = self.ids_of_players[self.number_of_mafiosi]
        self.id_of_doctor = self.ids_of_players[self.number_of_mafiosi+1]

        for player_id in self.ids_of_players:
            if player_id not in self.number_of_mafiosi:
                self.ids_of_innocents.append(player_id)
                
        self.message_for_group[0] = "The game of Mafia has started! \nThere are "+ str(self.number_of_mafiosi) +" mafiosi in the game."
        self.message_for_group[1] = None

        for player_id in self.ids_of_innocents:
            self.message_for_players[player_id] = ("You are Innocent\nYou win when all the mafia are lynched", None)
            
        for player_id in self.ids_of_mafiosi:
            self.message_for_players[player_id] = ("You are a member of the Mafia\nYou win when the mafia kill off all the innocents\nThe other mafiosi are:" 
                                                    + self.list_usernames([player_id], self.ids_of_mafiosi), None)

        self.message_for_players[self.id_of_detective] = ("You are the Detective\nYou win when all the mafia are lynched\nYou can to learn the role of another play every night", None)
        self.message_for_players[self.id_of_doctor] = ("You are the Doctor\nYou win when all the mafia are lynched\nYou can choose a player every night to keep alive", None)

        shuffle(self.ids_of_players)
        self.game_state = 2
        

    #   
    def setup_round(self):
        self.message_for_players = {}

        if self.game_state == 2:
            setup_night()
        if self.game_state == 3:
            setup_day()


    #
    def setup_night(self):
        self.message_for_group[0] = "The night has started, the mafia are plotting to kill someone"
        self.message_for_group[1] = None
                       
        markup_mafia = types.InlineKeyboardMarkup()
        for i in range(len(self.ids_of_innocents)):
            player_id = self.ids_of_innocents[i]
            player_id_index = str(i)
            #the code that chops up the callback data looks for two spaces
            if len(i) == 1:  
                player_id_index = "0" + player_id_index
            markup_mafia.row(types.InlineKeyboardButton(callback_data="kill"+ str(player_id_index) +str(key), text="@"+self.players_id_to_username[player_id]))

        markup_doctor = types.InlineKeyboardMarkup()
        markup_detective = types.InlineKeyboardMarkup()
        for i in range(len(self.ids_of_players)):
            player_id = self.ids_of_players[i]
            player_id_index = str(i)
            #the code that chops up the callback data looks for two spaces
            if len(i) == 1:  
                player_id_index = "0" + player_id_index
            markup_doctor.row(types.InlineKeyboardButton(callback_data="heal"+ str(player_id_index) +str(key), text="@"+self.players_id_to_username[player_id]))
            markup_detective.row(types.InlineKeyboardButton(callback_data="look"+ str(player_id_index) +str(key), text="@"+self.players_id_to_username[player_id]))

        self.ids_of_mafia_targets = {}

        for player_id in self.ids_of_mafiosi:
            self.message_for_players[player_id] = ("Who do you want to kill? Once all the mafia wants to kill the same person that person will be killed", markup_mafia)

        self.message_for_players[id_of_doctor] = ("Who do you want to heal?", markup_doctor)

        self.message_for_players[id_of_detective] = ("Who do you want to check the role of?", markup_detective)


    #
    def kill_vote_logic(self, mafia_id, id_of_player_voted_to_be_killed):
        self.ids_of_mafia_targets[mafia_id] = id_of_player_voted_to_be_killed

        markup_mafia = types.InlineKeyboardMarkup()
        
        for i in range(len(self.ids_of_innocents)):
            player_id = self.ids_of_innocents[i]
            
            player_id_index = str(i)
            if len(i) == 1:  
                player_id_index = "0" + player_id_index

            votes_for = ""
            for mafia_id in self.ids_of_mafia_targets:
                if self.ids_of_mafia_targets[mafia_id] == player_id:
                    votes_for += "+"

            markup_mafia.row(types.InlineKeyboardButton(callback_data="kill"+ str(player_id_index) +str(key), text="@"+self.players_id_to_username[player_id]+votes_for))

            if self.ids_of_mafia_targets.count(player_id) == self.number_of_mafiosi:
                if all(value == player_id for value in self.ids_of_mafia_targets.values()):
                    self.role_completed_mafia == True 
                
        for player_id in self.ids_of_mafiosi:
            self.message_for_players[player_id][1] = markup_mafia


    #
    def doctor_logic(self, id_of_player_to_save):
        self.role_completed_doctor = True

        self.id_of_saved_player = id_of_player_to_save
        return "@"+ self.players_id_to_username[id_of_player_to_save] +" will be saved"


    #
    def detective_logic(self, id_of_player_to_search):
        self.role_completed_detective = True

        if id_of_player_to_search in self.ids_of_innocents:
            if id_of_player_to_search == self.id_of_doctor:
                return "@"+ self.players_id_to_username[id_of_player_to_search] +" is the doctor."
            else:
                return "@"+ self.players_id_to_username[id_of_player_to_search] +" is an innocent towns person."
        if id_of_player_to_search in self.ids_of_mafiosi:
            return "@"+ self.players_id_to_username[id_of_player_to_search] +" is part of the mafia."


    #
    def night_over(self):
        if (self.role_completed_mafia 
        and self.role_completed_detective
        and self.role_completed_doctor):
            self.game_state = 3
            return True
        else:
            return False


    #
    def setup_day(self):
        id_of_victim = self.ids_of_mafia_targets.value()[0]

        victim_kill = id_of_victim != self.id_of_saved_player

        if victim_kill:
            self.message_for_group[0] = ""        
            
            self.ids_of_players.remove(id_of_victim)
            self.ids_of_innocents.remove(id_of_victim)
            self.number_of_players -= 1

        else:
            self.message_for_group[0] = ""


        markup_day = types.InlineKeyboardMarkup()
        for player_id in self.ids_of_players:
            markup_day.row(types.InlineKeyboardButton(callback_data="hang"+ str(player_id), text="@"+self.players_id_to_username[player_id]))

        self.message_for_group[1] = markup_day


    #
    def lych_nominate_logic(self, id_of_player_nominated_to_be_lyched):
        return


    #
    def lynch_vote_logic(self, id_of_player_voted_to_be_lyched):
        pass


    #
    def check_for_winner(self):
        pass

