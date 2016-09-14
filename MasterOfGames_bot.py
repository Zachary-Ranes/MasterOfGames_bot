#Written by Zachary Ranes
#Written for Python 3.4

import configparser
import telebot
from telebot import types
from MasterOfGames_bot_Games import Resistance
from MasterOfGames_bot_Games import GamePlayer

config = configparser.ConfigParser()
config.read("MasterOfGames_bot_config.cfg")

bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

games = {}


@bot.message_handler(commands=['start'])
def player_greatting(message):
    if message.chat.type == "private":
        bot.reply_to(message, "Hi (Placeholder)")		
        return

    if message.chat.type == "group" and message.chat.id not in games or message.chat.type == "supergroup" and message.chat.id not in games:
        bot.reply_to(message, "Hi (Placeholder)")
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


"""
@bot.message_handler(commands=['end_game'])
def end_game(message):
  bot.reply_to(message,
"""


@bot.message_handler(commands=['rules_resistance'])
def rules_for_resistance(message):
    bot.reply_to(message, "Da Rules (Placeholder)")


@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games and call.data == "resistance")
def new_game_of_resistance(call):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), types.InlineKeyboardButton(callback_data="start", text="Start Game"))
    bot.edit_message_text("You have selected the game resistance\nTo play resistance we need 5 to 10 people", message_id=call.message.message_id, 
                                                                                                                                                                                    chat_id=call.message.chat.id, 
                                                                                                                                                                                    reply_markup=markup)
    new_game = Resistance()
    games[call.message.chat.id] = new_game


@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "join")
def player_join_game(call):
    key = call.message.chat.id
    player_id = call.from_user.id

    if call.from_user.username == None:
        bot.send_message(key, "I am sorry "+ call.from_user.first_name +" but you must have an @UserName to play")
        return

    if len(games[key].players_id) == games[key].MAX_PLAYERS:
        bot.send_message(key, "I am sorry @"+ call.from_user.username +" but we already have the max number of player for this game")
        return

    if player_id not in games[key].players_id:  
        games[key].players_id.append(player_id)
        games[key].players[player_id] = GamePlayer()
        games[key].players[player_id].player_username = call.from_user.username
        games[key].player_usernames_to_id[call.from_user.username] = player_id
        bot.send_message(key, "@" +call.from_user.username +" has joined the game")
        #add this logic to a fuction in the Resistance class??


@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "start")
def start_game(call):
    key = call.message.chat.id

    if games[key].game_started != True:
        if len(games[key].players_id) < games[key].MIN_PLAYERS:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), types.InlineKeyboardButton(callback_data="start", text="Start Game"))
            try:
                bot.edit_message_text("Not enough players have joined to start the game \nYou need "+str(games[key].MIN_PLAYERS)
                                                    +" to "+str(games[key].MAX_PLAYERS)+" people to play, "+str(len(games[key].players_id))
                                                    +" players have joined", message_id=call.message.message_id, chat_id=key, reply_markup=markup)
            except:
                return

        if len(games[key].players_id) >= games[key].MIN_PLAYERS:
            bot.send_message(key, "Let the game begin (Placeholder)")
            game_startup_handler(key)
            return


def game_startup_handler(key):
    output_message = games[key].game_setup()
    talk_to_everyone = True

    for i in range(games[key].number_of_players):
        player_id = games[key].players_id[i]

        try:
            bot.send_message(player_id, games[key].players[player_id].roll_info)

        except:
            bot.send_message(key, "I can not talk to @" +games[key].players[player_id].player_username
                                                 +"\nPlease start a private chat with me then hit start again")
            talk_to_everyone = False

    if talk_to_everyone:		
        bot.send_message(key, output_message)
        games[key].game_started = True
        game_round_handler(key)


def game_round_handler(key):
    output_message = games[key].round_setup()
    bot.send_message(key, output_message)
  
    if games[key].game_over:
        del games[key]


@bot.message_handler(commands=['nominate'])
def nominate_players_for_mission(message):
    key = message.chat.id

    if key not in games:
        bot.reply_to(message, "No game in this chat right now")
        return

    if message.from_user.id == games[key].nominator_id and games[key].mission_state == 1:
        output_message = games[key].nominate_logic(message.entities, message.text)
        bot.reply_to(message, output_message)
        # write it so this can have an inline Yea or Nay buttons

"""
@bot.message_handler(commands=['Yea'])	
@bot.message_handler(commands=['Nay'])
def mission_vote(message):
    key = message.chat.id 
    player_id = message.from_user.id
  
    if key not in games:
        bot.reply_to(message, "No game in this chat right now")
        return

    if player_id in games[key].players_id and games[key].mission_state == 2:
        if message.text[1:4] == 'Yea': games[key].vote_logic(True, player_id)
        if message.text[1:4] == 'Nay': games[key].vote_logic(False, player_id)

        if games[key].mission_state == 1:
            bot.send_message(key, "Vote failed, New player will get to nominate")
            game_round_handler(key)

        if games[key].mission_state == 3:
            bot.send_message(key, "Vote passed, Now players will now go on a mission")
            #have this so it say who is leaving for the mission??
            game_mission_handler(key)

    else:
        bot.reply_to(message, "There's a time and place for everything, but not now")



def game_mission_handler(key)



@bot.message_handler(commands=['Pass'])	
@bot.message_handler(commands=['Fail'])
def game_mission_outcome(message)
  ?
"""



bot.polling()
