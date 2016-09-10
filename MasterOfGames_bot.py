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
state = {}
#state 0 = no game being run
#state 1 = game selection
#state 2 = players are joining game
#state 3 = game running



@bot.message_handler(commands=['start'])
def PlayerGreatting(message):
	if message.chat.type == "private":
		bot.reply_to(message, "Hi, bots are not alowed to message poeple that have not messaged them first ,that is why you have to start the chat with me to play the game\n To join type EXACTLY: /join #\n # = the number you got in the group chat")
		return
	
	if message.chat.type == "group" and message.chat.id not in state:
		state[message.chat.id] = 0
		return
		
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")
		

		
@bot.message_handler(commands=['new_game'])
def NewGame(message):
	if message.chat.type == "private":
		bot.reply_to(message, "You can't make a new game in a private chat")
		return
		
	if message.chat.type == "group" and message.chat.id not in state:
		state[message.chat.id] = 0
		
	if message.chat.type == "group" and state[message.chat.id] == 0:
		game_options = types.ReplyKeyboardMarkup()
		game_option1 = types.KeyboardButton('Resistance')
		game_options.row(game_option1)
		bot.reply_to(message, "Which game would you like to play?", reply_markup=game_options)
		state[message.chat.id] = 1
		return
		
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")
		
		

@bot.message_handler(func=lambda message: "Resistance" in message.text and state[message.chat.id] == 1)
def StartResistance(message):
	hide_options = types.ReplyKeyboardHide(selective=False)
	bot.reply_to(message, "You have selected the game resistance\nTo play resistance we need 5 to 10 people \nIf you want to play start a private chat with me and type EXACTLY: /join "+str(message.chat.id)+"\nOnce everyone is ready have someone type /start_game", reply_markup=hide_options)

	new_game = Resistance()
	new_game.game_room = message.chat.title
	games [message.chat.id] = new_game
	
	state[message.chat.id]  = 2

	
	
@bot.message_handler(commands=['join'])
def JoinGame(message):
	if message.chat.type != "private":
		bot.reply_to(message, "You must run the join command in a private chat with me ")
		return

	if message.chat.type == "private" and message.text.startswith("/join "):
		try:
			key = int(message.text[6:]) 
			
			if key not in state:
				bot.reply_to(message, "Sorry there is no game in that chat right now")
				return
			
			if state[key] != 2:
				bot.reply_to(message, "Sorry that chat's game can not be joined")
				return
			
			if state[key] == 2 and len(games[key].players) == games[key].MAXPLAYERS:
				bot.reply_to(message,"The game in that chat already has the max number of players")
				return
			
			if state[key] == 2 and message.from_user.id in games[key].players:
				bot.reply_to(message,"You have already joined the game in that chat")
				return
			
			if state[key] == 2:
				games[key].players.append(message.from_user.id)
				bot.reply_to(message, "you have joined the game")
				bot.send_message(key, message.from_user.first_name +" has joined the game")
		
		except:
			bot.reply_to(message, "Syntax Error!")
	
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")

		

@bot.message_handler(commands=['start_game'])
def StartGameResistance(message):
	if message.chat.type != "group":
		bot.reply_to(message, "You must be in a group chat to start a game")
		return
	
	if message.chat.id not in state:
		bot.reply_to(message, "Sorry there is no game in this chat right now")
		return
	
	if state[message.chat.id] != 2:
		bot.reply_to(message, "There's a time and place for everything, but not now")
		return
	
	if state[message.chat.id] == 2 :
		key = message.chat.id	
		
		if len(games[key].players) < games[key].MINPLAYERS:
			bot.reply_to(message, "Not enough players have joined to start the game \nYou need "+str(games[key].MINPLAYERS)+" to "+str(games[key].MAXPLAYERS)+" people to play, "+str(len(games[key].players))+" have joined")
			return
		
		if len(games[key].players) >= games[key].MINPLAYERS:
			bot.reply_to(message, "Let the game begin")
			state[message.chat.id]  = 3
			return
		
	else:
		bot.reply_to(message, "There's a time and place for everything, but not now")
		
	

		
bot.polling()
