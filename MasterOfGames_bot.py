#Written by Zachary Ranes
#Written for Python 3.4

import configparser
import telebot
from telebot import types
from MasterOfGames_bot_Games import Resistance
from MasterOfGames_bot_Games import ResistancePlayer

config = configparser.ConfigParser()
config.read("MasterOfGames_bot_config.cfg")

bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

games = {}


@bot.message_handler(commands=['start'])
def player_greatting(message):
	if message.chat.type == "private":
		bot.reply_to(message, "Hi, Placeholder")		
		return
	
	if message.chat.type == "group" and message.chat.id not in games or message.chat.type == "supergroup" and message.chat.id not in games:
		bot.reply_to(message, "Hi, Placeholder")
		return
		
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")

		

@bot.message_handler(commands=['new_game'])
def new_game(message):
	if message.chat.type == "private":
		bot.reply_to(message, "You can't make a new game in a private chat")
		return
		
	if message.chat.type == "group" and message.chat.id not in games or message.chat.type == "supergroup" and message.chat.id not in games:
		markup = types.InlineKeyboardMarkup()
		markup.row(types.InlineKeyboardButton(callback_data="resistance", text="Resistance"))
		bot.send_message(message.chat.id, "Which game would you like to play?", reply_markup=markup)
		return
		
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")
		
	
	
@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games and call.data == "resistance")
def start_resistance(call):
	markup = types.InlineKeyboardMarkup()
	markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), types.InlineKeyboardButton(callback_data="start", text="Start Game"))
	bot.edit_message_text("You have selected the game resistance\nTo play resistance we need 5 to 10 people", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)
	new_game = Resistance()
	games[call.message.chat.id] = new_game
	
	
	
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "join")
def player_join_game(call):
	key = call.message.chat.id
	player_id = call.from_user.id
	
	if player_id not in games[key].players_id: 
		games[key].players_id.append(player_id)
		games[key].players[player_id] = ResistancePlayer()
		games[key].players[player_id].player_username = call.from_user.username
		bot.send_message(key, "@" +call.from_user.username +" has joined the game")

	
	
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "start")
def start_game(call):
	key = call.message.chat.id
	game = games[key]
	
	if game.game_started != True:
		if len(game.players_id) < game.MINPLAYERS:
			markup = types.InlineKeyboardMarkup()
			markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), types.InlineKeyboardButton(callback_data="start", text="Start Game"))
			try:
				bot.edit_message_text("Not enough players have joined to start the game \nYou need "+str(game.MINPLAYERS)+" to "+str(game.MAXPLAYERS)+" people to play, "+str(len(game.players_id))+" players have joined", message_id=call.message.message_id, chat_id=key, reply_markup=markup)
			except:
				return
				
		if len(game.players_id) >= game.MINPLAYERS:
			bot.send_message(key, "Let the game begin, Placeholder")
			game_handler_one(key)
			return

			
	
def game_handler_one(key):
	games[key].set_up()
	game = games[key]
	talk_to_everyone = True
	
	for i in range(game.number_of_players):
		player_id = game.players_id[i]
		
		try:
			bot.send_message(player_id, game.players[player_id].roll_info)

		except:
			bot.send_message(key, "I can not talk to @" + game.players[player_id].player_username+ "\nPlease start a private chat with me then hit start again")
			talk_to_everyone = False
			
	if talk_to_everyone:		
		bot.send_message(key, game.game_info)
		game.game_started = True
		games[key] = game
			


		
		
bot.polling()
