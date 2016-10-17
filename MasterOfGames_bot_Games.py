#Author: Zachary Ranes
#Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

import math
from random import shuffle


class Game(object):
    
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
        self.number_of_players = None
        
        #
        self.players_id_to_username = {}
        self.players_username_to_id = {}
        
        #
        self.message_for_group = None
        self.message_for_players = {}
    
        
    #takes a telegram users chat ID,  username and first name
    #returns a message if success or there can be no more players or returns None if a message should not be sent
    def add_player(self, player_id, player_username, player_name):
        if player_username == None:
            return "I am sorry "+ player_name +" but you must have an @UserName to play"
        
        if len(self.ids_of_players) == self.MAX_PLAYERS:
            return "I am sorry @"+ player_username +" but we already have the max number of player for this game"
       
        if player_id not in self.ids_of_players: 
            self.ids_of_players.append(player_id)
            self.players_id_to_username[player_id] = player_username
            self.players_username_to_id[player_username] = player_id
            return "@"+ player_username +" has joined the game"
        
        else:
            return None
    
    
    #
    def enough_players(self):
        self.number_of_players = len(self.ids_of_players)
        
        if self.number_of_players < self.MIN_PLAYERS:
            return ("Not enough players have joined to start the game \nYou need "+str(self.MIN_PLAYERS)
                      +" to "+str(self.MAX_PLAYERS)+" people to play, "+str(self.number_of_players) +" players have joined")
        else:
            self.game_state = 1
            return None
        
        
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
    def list_usernames(self, exclude_id, list_of_player_ids):
        output = ""
        for player_id in list_of_player_ids:
            if player_id != exclude_id:
                output += " @" + players_id_to_username[player_id]
        return output
    
        
        
class Resistance(Game):

    def __init__(self, game_code = 1, min_players = 1, max_players = 10):
        super(Resistance, self).__init__(game_code, min_players, max_players)
   
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
        game_state is set to 0 in the parent class contructor
        
        game_state = 0 : game has not start (players can still join)
        game_state = 1 : the game has started (players cant hit join)
        game_state = 2 : looking for nominees for a mission
        game_state = 3 : looking for votes on nominees for mission
        game_state = 4 : voting over, players going on mission
        game_state = 5 : game has ending one team has scored 3 points
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
                
        self.message_for_group = "The game of Resistance has started! \nThere are "+ str(self.number_of_spies) +" spies in the game."
        
        for player_id in self.ids_of_resistances:
            self.message_for_players[player_id] = "You are part of the Resistance\nYou win when 3 missions succeed"
            
        for player_id in self.ids_of_spies:
            self.message_for_players[player_id] = "You are a Spy\n You win when 3 missions fail\nThe other spies are:" + self.list_usernames(player_id, ids_of_spies)

        #shuffled again so turn order does not give away roles
        shuffle(self.ids_of_players)

 
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
            extra_message = "This round requries two spys to vote for failure to fail\n"
        else:
            self.two_fail_mission = False
            extra_message = ""

        self.number_of_nominees = self.PLAYERS_PER_ROUND[self.number_of_players-self.MIN_PLAYERS][self.game_round]
        self.game_state = 2
        self.message_for_group = ("@"+ self.players_id_to_username[self.nominator_id] 
                                 +" gets to nominate "+ str(self.number_of_nominees) 
                                 +" players to go on the mission\n"+ extra_message
                                 +"Nominate players by typing /nominate (space) @username (space) @username ...etc")
    
    
    #
    def check_for_winner(self):
        if self.points_resistance == 3:
            self.game_state = 5
            self.message_for_group = "The resistance has scored 3 points!!!\nThe resistance has won the game"
            
        if self.points_spies == 3:
            self.game_state = 5
            self.message_for_group = "The spies have scored 3 points!!!\nThe spies have won the game"

                     
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
            return ("You nominated the wrong number of players\nYou need to nominate "+ str(self.number_of_nominees) 
                      +" players \nDo this by typing /nominate then the username of the players you want to nominate all in the same message")

        for i in range(len(mentioned)):
            if mentioned[i] not in self.players_username_to_id:
                return "You nominated someone not playing"
            if self.players_username_to_id[mentioned[i]] in self.ids_of_players_going_on_mission:
                return "You nominated someone more than once"
            else:
                self.ids_of_players_going_on_mission.append(self.players_username_to_id[mentioned[i]])

        self.ids_of_players_voted_on_nominees = []
        self.mission_yea_votes = 0
        self.mission_nay_votes = 0
        self.game_state = 3
        return "Now everyone vote on the proposed mission party\nIf half or more of the vote are nay the next player will get to nominate"

 """     
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

        output = "@"+ self.player_ids_to_username[player_id] +" has voted "+ vote
        self.players_id_voted_on_mission.append(player_id)
 
        return output
        
    
    #takes self
    #setup for var for a mission 
    def setup_mission(self):
        self.mission_pass_votes = 0
        self.mission_fail_votes = 0
        self.players_id_votes_from_mission = []
    
    
    #takes self and player chat id 
    #returns message of who else is on the current mission with them
    def mission_info(self, player_id):
        output = "You are on a mission with "

        if player_id == None:
            output = "Enough yeas have been cast, "
                
        for i in range(len(self.players_id_going_on_mission)):
            if player_id != self.players_id_going_on_mission[i]:
                output += " @" + self.player_ids_to_username[self.players_id_going_on_mission[i]] 
                    
        if player_id == None:
            output += " are now going to go on a mission"
                
        return output
    
    
    #takes self, players id and string that is there vote on whether the mission passes or not
    #changes games state to 2 if the voting round is over or to state 5 if that was the last round
    #returns two outputs the first being a message if a mission failed or not and the second being a message about the game ending
    def mission_logic(self, player_id, vote):
        if vote == "pass":
            self.mission_pass_votes += 1
        
        if vote == "fail" and player_id in self.spys_id:
            self.mission_fail_votes += 1
        
        self.players_id_votes_from_mission.append(player_id)

        output = None

        if len(self.players_id_going_on_mission) == len(self.players_id_votes_from_mission):
           
            if (self.mission_fail_votes >= 1 and self.two_fail_mission == False 
             or self.mission_fail_votes >= 2 and self.two_fail_mission == True):
                self.points_spys += 1
                output = ("Mission fails !!!!!\n") 
                         
            else:
                self.points_resistance += 1
                output =  ("Mission passed!!!! \n")

            self.game_round += 1
            output += ("The score is now:\n "
                        + str(self.points_resistance) +" for the Resistance \n"
                        + str(self.points_spys) +" for the Spies")
            self.game_state = 2
            
            if self.points_spys == 3 or self.points_resistance == 3:
                self.game_state = 5
            
            
        return output
    



"""

class Mafia(Game):
    pass
