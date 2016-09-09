#Written by Zachary Ranes
#Written for Python 3.4

import configparser
import telebot
import math
import random

config = configparser.ConfigParser()
config.read("MasterOfGames_bot_config.cfg")

bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

bot.game_state = 0
bot.players = []
bot.spys= []
bot.game_room = None
bot.number_of_players = None
bot.number_of_spys = None
bot.round_number = None
bot.points_resistance = 0
bot.points_spys = 0



@bot.message_handler(commands=['start'])
def NewPlayer(message):
	if message.chat.type == "group":
		bot.reply_to(message, "Hi I am a bot that lets you play games in a chat group \nRun the /new_game command to begin a new game")
	
	if message.chat.type == "private":
		bot.reply_to(message, "Hi, bots are not alowed to message poeple that have not messaged them first ,that is why you have to start the chat with me to play the game\nDo not forget to run the /join command")

		

@bot.message_handler(commands=['new_game'])
def NewGame(message):
	if message.chat.type == "private":
		bot.reply_to(message, "You can't make a new game in a private chat")
		return
		
	if message.chat.type != "private" and bot.game_state > 0:
		bot.reply_to(message, "There is a game already made")
		return
	
	if message.chat.type != "private" and bot.game_state ==0:
		bot.reply_to(message, "To play resistance we need 5 to 10 people \nIf you want to play type /join in a private chat with me\nOnce everyone is ready have someone run the /start_game")
		bot.game_room = message.chat.id 
		bot.game_state = 1
		
		
	
	
@bot.message_handler(commands=['join'])
def JoinGameResistance(message):
	if message.chat.type != "private":
		bot.reply_to(message, "Sorry you must run the join command in a private chat with me")
		return
	
	if len(bot.players) == 10:
		bot.reply_to(message, "The game already has the max number of players")
		return
	
	if bot.game_state > 1:
		bot.reply_to(message, "The game has already started")
		return
		
	if bot.game_state <= 0:
		bot.reply_to(message, "There is no game to join")
		return
		
	if bot.game_state == 1 and message.from_user.id in bot.players:
		bot.reply_to(message, "You have already joined the game")		
		return
		
	if bot.game_state == 1 and message.from_user.id not in bot.players:
		bot.reply_to(message, "You have joined the game")
		bot.send_message(bot.game_room, message.from_user.first_name +" has joined the game")
		bot.players.append(message.from_user.id)

		
		
@bot.message_handler(commands=['start_game'])
def StartGameResistance(message):
	if bot.game_state <= 0:
		bot.reply_to(message, "There is no game to start")
		return
	
	if bot.game_state > 1 and message.chat.id == bot.game_room:
		bot.reply_to(message, "The game has already started")
		return
		
	if bot.game_state == 1 and message.chat.id == bot.game_room and len(bot.players) < 5:
		bot.reply_to(message, "Not enough players have joined to start the game \nYou need 5 to 10 people to play, "+str(len(bot.players))+" have joined")
		return
		
	if bot.game_state == 1 and message.chat.id == bot.game_room and len(bot.players) >= 5 :
		bot.reply_to(message, "Let the game begin")
		bot.game_state = 2
		AssignRoles()
		return
		
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")
	

		
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
"""	
	#GameHandler()
		
		

def GameHandler():
	bot.round_number = 0
	while bot.points_resistance < 3 and bot.points_spys <3:
		RoundHandler(bot.round_number)
		bot.round_number += 1
	
	if bot.points_resistance == 3
	if bot.points_spys == 3
"""
	
	
		
bot.polling()
