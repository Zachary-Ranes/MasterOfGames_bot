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
bot.game_room = None
bot.number_of_players = None
bot.number_of_spys = None



@bot.message_handler(commands=['start'])
def new_player(message):
	if message.chat.type == "group":
		bot.reply_to(message, "Hi I am a bot that lets you play games in a chat group \nRun the /new_game command to begin a new game")
	if message.chat.type == "private":
		bot.reply_to(message, "Hi, bots are not alowed to message poeple that have not messaged them first ,that is why you have to start the chat with me to play the game\nDo not forget to run the /join command")

		

@bot.message_handler(commands=['new_game'])
def new_game_resistance(message):
	if message.chat.type == "private":
		bot.reply_to(message, "You can't make a new game in a private chat")
	elif message.chat.type != "private" and bot.game_state > 0:
		bot.reply_to(message, "There is a game already made")
	elif message.chat.type != "private" and bot.game_state ==0:
		bot.reply_to(message, "To play resistance we need 5 to 10 people \nIf you want to play type /join in a private chat with me\nOnce everyone is ready have someone run the /start_game")
		bot.game_room = message.chat.id 
		bot.game_state = 1
		
		
	
	
@bot.message_handler(commands=['join'])
def join_game_resistance(message):
	if message.chat.type != "private":
		bot.reply_to(message, "Sorry you must run the join command in a private chat with me")
	elif len(bot.players) == 10:
		bot.reply_to(message, "The game already has the max number of players")
	elif bot.game_state > 1:
		bot.reply_to(message, "The game has already started")
	elif bot.game_state == 0:
		bot.reply_to(message, "There is no game to join")
	elif bot.game_state == 1 and message.from_user.id in bot.players:
		bot.reply_to(message, "You have already joined the game")		
	elif bot.game_state == 1 and message.from_user.id not in bot.players:
		bot.reply_to(message, "You have joined the game")
		bot.send_message(bot.game_room, message.from_user.first_name +" has joined the game")
		bot.players.append(message.from_user.id)

		
		
@bot.message_handler(commands=['start_game'])
def start_game_resistance(message):
	if bot.game_state > 0: 
		if bot.game_state > 1 and message.chat.id == bot.game_room:
			bot.reply_to(message, "The game has already started")
		if bot.game_state == 1 and message.chat.id == bot.game_room and len(bot.players) < 5:
			bot.reply_to(message, "Not enough players have joined to start the game \nYou need 5 to 10 people to play, "+str(len(bot.players))+" have joined")
		if bot.game_state == 1 and message.chat.id == bot.game_room and len(bot.players) >= 5 :
			bot.reply_to(message, "Let the game begin")
			bot.game_state = 2
			assign_roles()
		else:
			bot.reply_to(message, "There's a time and place for everything, but not now")
	else:
		bot.reply_to(message, "There is no game to start")
		
		
		
def assign_roles():
		bot.number_of_players = len(bot.players)
		bot.number_of_spys = int(math.ceil(bot.number_of_players/3))
		
		random.shuffle(bot.players)
		
		bot.send_message(bot.game_room, "There are will be "+str(bot.number_of_spys)+" Spys in this game" )
		bot.send_message(bot.players[0], "You are a Spy")
		bot.send_message(bot.players[1], "You are a Spy")
		bot.send_message(bot.players[2], "You are Resistance")
		bot.send_message(bot.players[3], "You are Resistance")
		bot.send_message(bot.players[4], "You are Resistance")
		

			
		
bot.polling()
