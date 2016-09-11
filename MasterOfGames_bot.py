#Written by Zachary Ranes
#Written for Python 3.4

import configparser
import telebot
from telebot import types
from MasterOfGames_bot_Games import Resistance

config = configparser.ConfigParser()
config.read("MasterOfGames_bot_config.cfg")

bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

games = {}


@bot.message_handler(commands=['start'])
def player_greatting(message):
	if message.chat.type == "private":
		bot.reply_to(message, "Hi, Placeholder")
		return
	
	if message.chat.type == "group" and message.chat.id not in games:
		bot.reply_to(message, "Hi, Placeholder")
		return
		
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")
		

@bot.message_handler(commands=['new_game'])
def new_game(message):
	if message.chat.type == "private":
		bot.reply_to(message, "You can't make a new game in a private chat")
		return
		
	if message.chat.type == "group" and message.chat.id not in games:
		markup = types.InlineKeyboardMarkup()
		markup.row(types.InlineKeyboardButton(callback_data="resistance", text="Resistance"))
		bot.reply_to(message, "Which game would you like to play?", reply_markup=markup)
		return
		
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")
		
		
@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games and call.data == "resistance")
def start_resistance(call):
	markup = types.InlineKeyboardMarkup()
	markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), types.InlineKeyboardButton(callback_data="start", text="Start Game"))
	bot.send_message(call.message.chat.id, "You have selected the game resistance\nTo play resistance we need 5 to 10 people", reply_markup=markup)
	new_game = Resistance()
	games[call.message.chat.id] = new_game
	
	
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "join")
def player_join_game(call):
	key = call.message.chat.id
	player = call.from_user
	if player.id not in games[key].players: 
		games[key].players.append(player.id)
		bot.send_message(key, player.first_name +" has joined the game")

	
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "start")
def start_game(call):
	key = call.message.chat.id
	game = games[key]
	if game.game_started != True:
		if len(game.players) < game.MINPLAYERS:
			bot.send_message(key, "Not enough players have joined to start the game \nYou need "+str(game.MINPLAYERS)+" to "+str(game.MAXPLAYERS)+" people to play, "+str(len(game.players))+" have joined")
			return
		
		if len(game.players) >= game.MINPLAYERS:
			bot.send_message(key, "Game start, Placeholder")
			game_handler(key)
			return

	
def game_handler(key):
	games[key].SetUp()
	game = games[key]
	for i in range(game.number_of_players):
		player_id = game.players[i]
		bot.send_message(player_id, game.player_rolls[player_id].roll_info)
	bot.send_message(key, game.game_info)


		
bot.polling()
