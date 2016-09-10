#Written by Zachary Ranes
#Written for Python 3.4

import math
from random import shuffle

class ResistanceRoll

	def __init__(self):
		self.spy = False
		self.roll_info = None

class Resistance:
	
	MINPLAYERS = 5
	MAXPLAYERS = 10
	
	def __init__(self):
		self.players = []
		self.rolls = {}
		self.game_info = None		

	def StartUp():
		





#code frags not yet uesed 
"""

bot.players = []
bot.spys= []
bot.game_room = None
bot.number_of_players = None
bot.number_of_spys = None
bot.round_number = None
bot.points_resistance = 0
bot.points_spys = 0


def AssignRoles():
	bot.number_of_players = len(bot.players)
	bot.number_of_spys = int(math.ceil(bot.number_of_players/3))
	
	random.shuffle(bot.players)
	
	bot.send_message(bot.game_room, "There are will be "+str(bot.number_of_spys)+" Spys in this game" )
	
	for i in range(bot.number_of_spys):
		bot.send_message(bot.players[i], "You are a Spy")
		bot.spys.append(bot.players[i])
	
	index_shift = bot.number_of_players - bot.number_of_spys - 1
	for i in range(bot.number_of_players - bot.number_of_spys):
		bot.send_message(bot.players[i + index_shift], "You are Resistance")

		
	GameHandler()
		
		

def GameHandler():
	bot.round_number = 0
	while bot.points_resistance < 3 and bot.points_spys <3:
		RoundHandler(bot.round_number)
		bot.round_number += 1
	
	if bot.points_resistance == 3
	if bot.points_spys == 3

	
"""
