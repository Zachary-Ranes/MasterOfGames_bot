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
    self.PLAYERS_PER_ROUND = [self.FIVE_PLAYERS, self.SIX_PLAYERS, self.SEVEN_PLAYERS, self.EIGHT_PLUS_PLAYERS, self.EIGHT_PLUS_PLAYERS, self.EIGHT_PLUS_PLAYERS]

    self.players_id = []
    self.players = {}
    self.player_usernames_to_id = {}

    #these two and mission _state should be one game state var
    self.game_started = False
    self.game_over = False

    self.number_of_players = None
    self.number_of_spys = None
    self.spys_id = []	

    self.round = 0
    self.nominator_id = None
    self.last_nominator_index = -1
    self.number_of_nominees = None
    self.two_fail_mission = None
    self.mission_players_id = []

    self.mission_state = 0
    """
    State 0 not looking for any user input on missions
    State 1 looking for noninees
    State 2 looking for votes on nominees
    State 3 looking for votes from players on mission
    """

    self.players_voted_on_mission = []
    self.mission_yea_votes = 0
    self.mission_nay_votes = 0

    self.points_spys = 0
    self.points_resistance = 0


  def game_setup(self):
    self.number_of_players = len(self.players_id)
    self.number_of_spys = int(math.ceil(self.number_of_players/3))
    shuffle(self.players_id)

    for i in range(self.number_of_spys):
      player_id = self.players_id[i]
      self.spys_id.append(player_id)
      player = self.players[player_id]
      player.spy = True
      player.roll_info = "You are a Spy\nThe spys in this game are:\n"
      self.players[player_id] = player

    #this whole chuck feels sloppy
    list_of_spys_string = ""
    for i in range(self.number_of_spys):
      list_of_spys_string += "@" + self.players[self.spys_id[i]].player_username + " "
    for i in range(self.number_of_spys):
      self.players[self.spys_id[i]].roll_info += list_of_spys_string


    index_shift = self.number_of_players - self.number_of_spys - 1
    for i in range(self.number_of_players - self.number_of_spys):
      player_id = self.players_id[i + index_shift]
      player = self.players[player_id]
      player.roll_info = "You are part of the Resistance"
      self.players[player_id] = player

    shuffle(self.players_id)
    return "There are "+str(self.number_of_spys) +" spys in the game"


  def round_setup(self):
    if self.last_nominator_index == -1 or self.last_nominator_index + 1 == self.number_of_players:
      self.last_nominator_index == 0
      self.nominator_id = self.players_id[0]

    else:
      self.last_nominator_index += 1
      self.nominator_id = self.player_id[self.last_nominator_index]

    if self.round == 3 and self.number_of_players >= 7:
      self.two_fail_mission = True
      extra_message = "This round requries two spys to vote for failure to fail\n"
    else:	
      self.two_fail_mission = False
      extra_message = ""

    if self.points_spys == 3:
      self.game_over = True
      return "The game is over the Spys wins!!!" 

    if self.points_resistance == 3:
      self.game_over = True
      return "The game is over the Resistance wins!!!"

    if self.points_spys < 3 and self.points_resistance < 3:
      self.number_of_nominees = self.PLAYERS_PER_ROUND[self.number_of_players-self.MIN_PLAYERS][self.round]
      self.mission_state = 1
      return "@"+ self.players[self.nominator_id].player_username +" gets to nominate "+ str(self.number_of_nominees) +" players to go on the mission\n"+extra_message+"Nominate players by typing /nominate @player_username"


  def nominate_logic(self, entities, text):
    mentioned = []
    self.mission_players_id = []
    for i in range(len(entities)):
      if entities[i].type == "mention":
        starting_index = entities[i].offset +1
        ending_index = entities[i].offset + entities[i].length
        username_without_at = text[starting_index:ending_index]
        mentioned.append(username_without_at)

    if len(mentioned) != self.number_of_nominees:
      return "You nominated the wrong number of players\nYou need to nominate "+ str(self.number_of_nominees) + " players \nDo this by typing /nominate then the username of the players you want to nominate all in the same message"

    for i in range(len(mentioned)):
      if mentioned[i] not in self.player_usernames_to_id:
        return "You nominated someone not playing"
      else:
        self.mission_players_id.append(self.player_usernames_to_id[mentioned[i]])

    self.players_voted_on_mission = []
    self.mission_yea_votes = 0
    self.mission_nay_votes = 0
    self.mission_state = 2
    return "Okay now everyone vote /Yea or /Nay for the nominated party"

"""
  def vote_logic(self, voted_yea, player_id):
    if player_id not in self.players_voted_on_mission:
      if voted_yea:
        self.mission_yea_votes += 1
        self.players_voted_on_mission.append(player_id)

      else:
        self.mission_nay_votes += 1
        self.players_voted_on_mission.append(player_id)

    if self.mission_nay_votes >= self.number_of_players/2:
      self.mission_state == 1
      return

    if self.mission_yea_votes > self.number_of_players/2:
      self.mission_state == 3
"""
