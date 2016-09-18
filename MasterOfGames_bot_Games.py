#Written by Zachary Ranes
#Written for Python 3.4

import math
from random import shuffle
        
class Resistance:

    def __init__(self):
        self.MIN_PLAYERS = 5
        self.MAX_PLAYERS = 10

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

        self.game_state = 0
        self.game_state_holder = None
        """
        state 0 = game has not start (players can still join)
        state 1 = the game has started (players cant hit join)
        state 2 = looking for nominess for a mission
        state 3 = looking for votes on nominess for mission
        state 4 = votings over, players going on mission
        state 5 = game has ending one team has scored 3 points
        state 6 = 
        state 7 = game is paused (waiting for the game to be ended or continued)
        """
        self.round = 0
                
        self.players_id = []
        self.number_of_players = 0
        self.spys_id = []	
        self.number_of_spys = 0
        
        self.player_ids_to_username = {}
        self.player_usernames_to_id = {}

        self.nominator_id = None
        self.last_nominator_index = 0
        
        self.number_of_nominees = None
        self.two_fail_mission = False
        
        self.players_id_going_on_mission = []
        
        self.players_id_voted_on_mission = []
        self.mission_yea_votes = 0
        self.mission_nay_votes = 0
        
        self.players_id_votes_from_mission = []
        self.mission_fail_votes = 0
        self.mission_pass_votes = 0
        
        self.points_spys = 0
        self.points_resistance = 0

        
        
    #takes a telegram users chat ID,  username and first name
    #returns a message if succes or there can be no more players or returns None if a message should not be sent
    def add_player(self, player_id, player_username, player_name):
        if player_username == None:
            return "I am sorry "+ player_name +" but you must have an @UserName to play"
        
        if len(self.players_id) == self.MAX_PLAYERS:
            return "I am sorry @"+ player_username +" but we already have the max number of player for this game"
       
        if player_id not in self.players_id: 
            self.players_id.append(player_id)
            self.player_ids_to_username[player_id] = player_username
            self.player_usernames_to_id[player_username] = player_id
            return "@"+ player_username +" has joined the game"
        
        else:
            return None

            
    
    #uses internal var 
    #returns a messege of number of playres lacking or changes game_state to 1 and returns number of spicy in the game string
    def setup_game(self):
        self.number_of_players = len(self.players_id)
        
        if self.number_of_players < self.MIN_PLAYERS:
            return ("Not enough players have joined to start the game \nYou need "+str(self.MIN_PLAYERS)
                      +" to "+str(self.MAX_PLAYERS)+" people to play, "+str(self.number_of_players) +" players have joined")
        
        self.number_of_spys = int(math.ceil(self.number_of_players/3))
        #shuffling user IDs so the roles are not deturmind by what order poeple joined the game
        shuffle(self.players_id)

        self.spys_id = []
        for i in range(self.number_of_spys):
            self.spys_id.append(self.players_id[i])

        #shufled again so turn order does not give away roles
        shuffle(self.players_id)
        self.game_state = 1
        return "The game of Resistance has started! \nThere are "+str(self.number_of_spys) +" spys in the game"
    
 

    #pause games 
    def pause_game(self, value):
        if value == True:
            self.game_state_holder = self.game_state
            self.game_state = 7
        if value == False:
            self.game_state = self.game_state_holder
            self.game_state_holder = None



    #take self and player chat id 
    #returns what roll in the game the player is and if spy who the other spys are
    def player_roll_info(self, player_id):
        if player_id not in self.spys_id:
            return "You are part of the Resistance"
        else:
            output = "You are a Spy\nThe other spy in this game are:\n"
            for i in range(len(self.spys_id)):
                if player_id != self.spys_id[i]:
                    output += "@" + str(self.player_ids_to_username[self.spys_id[i]]) + "\n"
            return output
        
        
    #takes self
    #return message who gets to nominate and if there are specail rules this round
    def setup_round(self):
        self.nominator_id = self.players_id[self.last_nominator_index]   
         
        self.last_nominator_index += 1
        
        if self.last_nominator_index == self.number_of_players:
            self.last_nominator_index == 0
        

        #This if else is for the rule that some misions in the game will need two fail votes to fail
        if self.round == 3 and self.number_of_players >= 7:
            self.two_fail_mission = True
            extra_message = "This round requries two spys to vote for failure to fail\n"
        else:	
            self.two_fail_mission = False
            extra_message = ""

        self.number_of_nominees = self.PLAYERS_PER_ROUND[self.number_of_players-self.MIN_PLAYERS][self.round]
        self.game_state = 2
        return ("@"+ self.player_ids_to_username[self.nominator_id] 
                   +" gets to nominate "+ str(self.number_of_nominees) 
                   +" players to go on the mission\n"+ extra_message
                   +"Nominate players by typing /nominate (space) @username (space) @username ...etc")


                       
    #takes self an array of telegram chat entities and a chat messages text
    #returns message about wether the message was a valid nomination
    def nominate_logic(self, entities, text):
        mentioned = []
        self.players_id_going_on_mission = []
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
            if mentioned[i] not in self.player_usernames_to_id:
                return "You nominated someone not playing"
            if self.player_usernames_to_id[mentioned[i]] in self.players_id_going_on_mission:
                return "You nominated someone more than once"
            else:
                self.players_id_going_on_mission.append(self.player_usernames_to_id[mentioned[i]])

        self.players_id_voted_on_mission = []
        self.mission_yea_votes = 0
        self.mission_nay_votes = 0
        self.game_state = 3
        return "Now everyone vote on the proposed mission party\nIf half or more of the vote are nay the next player will get to nominate"


    
    #takes self, telegram user id and callback data (a string)
    #does calculation, retunres message if votes chnages state
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
    
    
    
    #takes self, players id and string that is there vote on wether the mission passes or not
    #changes games state to 2 if the voting round is over or to state 5 if that was the last round
    #retuns two outputs the first being a message if a mission failed or not and the secound being a message about the game ending
    def mission_logic(self, player_id, vote):
        if vote == "pass":
            self.players_id_votes_from_mission.append(player_id)
            self.mission_pass_votes += 1
        
        if vote == "fail" and player_id in self.spys_id:
            self.players_id_votes_from_mission.append(player_id)
            self.mission_fail_votes += 1

        output1 = None
        output2 = None
        
        if len(self.players_id_going_on_mission) == len(self.players_id_votes_from_mission):
            if (self.mission_fail_votes >= 1 and self.two_fail_mission == False 
             or self.mission_fail_votes >= 2 and self.two_fail_mission == True):
                self.points_spys += 1
                self.round += 1
                self.game_state = 2 
                output1 = ("Mission fails !!!!!\n" + str(self.mission_fail_votes) + " fail vote(s) were handed in \nThe score is now "
                                + str(self.points_resistance) +" for the Resistance and "+ str(self.points_spys) +" for the Spys")
                
                if self.points_spys == 3:
                    self.game_state = 5
                    output2 = "The Spys win the game"
                         
            else:
                self.points_resistance += 1
                self.round += 1
                self.game_state = 2
                output1 =  ("Mission passed!!!! \n" + str(self.mission_fail_votes) + " fail vote(s) were handed in \nThe score is now "
                                + str(self.points_resistance) +" for the Resistance and "+ str(self.points_spys) +" for the Spys")
                
                if self.points_resistance == 3:
                    self.game_state = 5
                    output2 = "The Resistance wins the game"
         
        return output1, output2
    
     
    
    
