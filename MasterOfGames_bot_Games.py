#Written by Zachary Ranes
#Written for Python 3.4

import math
import telebot
from random import shuffle

class GamePlayer:
    def __init__(self):
        self.player_username = None
        self.spy = False
        self.roll_info = None

class Resistance:

    def __init__(self):
        self.MIN_PLAYERS = 3 #should be 5 but lower for testing
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

        self.players_id = []
        self.players = {}
        self.player_usernames_to_id = {}

        self.number_of_players = None
        self.number_of_spys = None
        self.spys_id = []	

        self.round = 0
        self.game_state = 0
        """
        state 0 = game has not start (players can still join)
        state 1 = the game has started (players cant hit join)
        state 2 = looking for nominess for a mission
        state 3 = looking for votes on nominess for mission
        state 4 = votings over, players going on mission
        state 5 =
        state 6 = game has ending one team has scored 3 points
        """
        
        self.nominator_id = None
        self.last_nominator_index = -1
        
        self.number_of_nominees = None
        self.two_fail_mission = None
        self.players_going_on_mission = []

        self.players_voted_on_mission = []
        self.mission_yea_votes = 0
        self.mission_nay_votes = 0

        self.points_spys = 0
        self.points_resistance = 0


    def game_setup(self):
        self.number_of_players = len(self.players_id)
        self.number_of_spys = int(math.ceil(self.number_of_players/3))
        #shuffling user IDs so the roles are not deturmind by what order poeple joined the game
        shuffle(self.players_id)

        for i in range(self.number_of_spys):
            player_id = self.players_id[i]
            self.spys_id.append(player_id)
            self.players[player_id].spy = True
            self.players[player_id].roll_info = "You are a Spy\nThe spys in this game are:\n"

        list_of_spys_string = ""
        for i in range(self.number_of_spys):
            list_of_spys_string += "@" + self.players[self.spys_id[i]].player_username + " "
        for i in range(self.number_of_spys):
            self.players[self.spys_id[i]].roll_info += list_of_spys_string


        index_shift = self.number_of_players - self.number_of_spys - 1
        for i in range(self.number_of_players - self.number_of_spys):
            player_id = self.players_id[i + index_shift]
            self.players[player_id].roll_info = "You are part of the Resistance"

        #shufled again so turn order does not give away roles
        shuffle(self.players_id)
        return "The game of Resistance has started! \nThere are "+str(self.number_of_spys) +" spys in the game"


    def round_setup(self):
        if self.last_nominator_index == -1 or self.last_nominator_index + 1 == self.number_of_players:
            self.last_nominator_index == 0
            self.nominator_id = self.players_id[0]

        else:
            self.last_nominator_index += 1
            self.nominator_id = self.player_id[self.last_nominator_index]

        #This if else is for the rule that some misions in the game will need two fail votes to fail
        if self.round == 3 and self.number_of_players >= 7:
            self.two_fail_mission = True
            extra_message = "This round requries two spys to vote for failure to fail\n"
        else:	
            self.two_fail_mission = False
            extra_message = ""

        if self.points_spys == 3:
            self.game_state = 6
            return "The game is over the Spys wins!!!" 
        if self.points_resistance == 3:
            self.game_state = 6
            return "The game is over the Resistance wins!!!"

        if self.points_spys < 3 and self.points_resistance < 3:
            self.number_of_nominees = self.PLAYERS_PER_ROUND[self.number_of_players-self.MIN_PLAYERS][self.round]
            self.game_state = 2
            return ("@"+ self.players[self.nominator_id].player_username 
                       +" gets to nominate "+ str(self.number_of_nominees) 
                       +" players to go on the mission\n"+ extra_message
                       +"Nominate players by typing /nominate (space) @username (space) @username ...etc")


    def nominate_logic(self, entities, text):
        mentioned = []
        self.players_going_on_mission = []
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
            else:
                self.players_going_on_mission.append(self.player_usernames_to_id[mentioned[i]])

        self.players_voted_on_mission = []
        self.mission_yea_votes = 0
        self.mission_nay_votes = 0
        self.game_state = 3
        return "Now everyone vote on the proposed mission party\nIf half or more of the vote are nay the next player will get to nominate"


    
    
    
    