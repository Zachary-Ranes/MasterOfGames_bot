#Written by Zachary Ranes
#Written for Python 3.4

import math
from random import shuffle

class Roll:

	def __init__(self):
		self.spy = False
		self.roll_info = None

class Resistance:
	
	MINPLAYERS = 5
	MAXPLAYERS = 10
	
	def __init__(self):
		self.players = []
		self.player_rolls = {}
		self.number_of_players = None
		self.number_of_spys = None
		self.game_info = None		
		
	def StartUp():
		self.number_of_players = len(self.players)
		self.number_of_spys = int(math.ceil(number_of_players/3))
		random.shuffle(self.players)
		
		for i in range(self.number_of_spys):
			player_id = self.players[i]
			player_roll = Roll()
			player_roll.spy = True
			player_roll.roll_info = "Your are a Spy"
			self.player_rolls[player_id] = player_roll
		
		index_shift = self.number_of_players - self.number_of_spys - 1
		for i in range(self.number_of_players - self.number_of_spys):
			player_id = self.players[i + index_shift]
			player_roll = Roll()
			player_roll.roll_info = "You are part of the Resistance"
			self.player_rolls[player_id] = player_roll
		
		self.game_info = "There are "+str(self.number_of_spys) +" spys in the group"




