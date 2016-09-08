#Written by Zachary Ranes
#Written for Python 3.4

import telebot
import random 
import math

bot = telebot.TeleBot("294917770:AAHY8k4oLdBN-3haU29_Tywp0xXbScWGjps")
bot.game_state = 0
bot.players = []



@bot.message_handler(commands=['new_game'])
def new_game_resistance(message):
	bot.reply_to(message, "To play resistance we need 5 to 10 people \nIf you want to play type /join \nOnce everyone that wants to play has joined have someone run the /start_game")
	bot.game_state = 1

@bot.message_handler(commands=['join'])
def join_game_resistance(message):
	if len(bot.players) == 10:
		bot.reply_to(message, "This game already has the max number of players")
	elif bot.game_state > 1:
		bot.reply_to(message, "There is a game already started \nYou can not join a game already started")
	elif bot.game_state == 1 and message.from_user.id in bot.players:
		bot.reply_to(message, "You have already joined the game")		
	elif bot.game_state == 1 and message.from_user.id not in bot.players:
		bot.reply_to(message, "You have joined the game")
		bot.players.append(message.from_user.id)
	else:
		bot.reply_to(message, "There is no game to join")

@bot.message_handler(commands=['start_game'])
def start_game_resistance(message):
	if bot.game_state == 1 and len(bot.players) < 5:
		bot.reply_to(message, "Not enough players have joined to start the game \nYou need 5 to 10 people to play, there are "+str(len(bot.players))+" playing now")
	if bot.game_state == 1 and len(bot.players) >= 5:
		bot.reply_to(message, "Let the game begine")
		bot.game_state = 2
		assign_roles()
		
		
def assign_roles()
		random.shuffle(bot.players)
		number_of_players = len(bot.players)
		number_of_spys = int(math.ciel(number_of_players/3))

		
		
		
		
bot.polling()
