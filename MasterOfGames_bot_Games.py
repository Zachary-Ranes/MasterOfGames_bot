#Written by Zachary Ranes
#Written for Python 3.4

import math
from random import shuffle

class GamePlayer:

	def __init__(self):
		self.player_username = None
		self.spy = False
		self.roll_info = None

class Resistance:
	
	MINPLAYERS = 3 #should be 5 but is set to 3 for testing
	MAXPLAYERS = 10
	
	def __init__(self):
		self.players_id = []
		self.players = {}
		self.game_started = False
		self.number_of_players = None
		self.number_of_spys = None
		self.spys_id = []
		self.game_info = None		
		self.points_spys = 0
		self.points_resistance = 0
		
		
	def set_up(self):
		self.number_of_players = len(self.players_id)
		self.number_of_spys = int(math.ceil(self.number_of_players/3))
		shuffle(self.players_id)
		
		for i in range(self.number_of_spys):
			player_id = self.players_id[i]
			player = self.players[player_id]
			player.spy = True
			player.roll_info = "You are a Spy"
			self.spys_id.append(player_id)
			self.players[player_id] = player
		
		index_shift = self.number_of_players - self.number_of_spys - 1
		for i in range(self.number_of_players - self.number_of_spys):
			player_id = self.players_id[i + index_shift]
			player = self.players[player_id]
			player.roll_info = "You are part of the Resistance"
			self.players[player_id] = player
		
		self.game_info = "There are "+str(self.number_of_spys) +" spys in the game (Placeholder)"
		
		




