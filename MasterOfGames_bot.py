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

#This dictionary holds the game object that hold all the info about game state, the group chat that the bot is playng the game in is the key
games = {}


#responce to the command that is run when the bot is first talked to by user and first added to groupchats 
@bot.message_handler(commands=['start'])
def start_command_handler(message):
    if message.chat.type == "private":
        bot.reply_to(message, "Hello, I can now talk with you.\nIf you are not part of a game go to a group chat and run /start")		
        return

    if message.chat.type == "group" and message.chat.id not in games or message.chat.type == "supergroup" and message.chat.id not in games:
        bot.reply_to(message, "Hello!!! if you would like to play a game run /new_game")
        return
    
    else:
        bot.reply_to(message, "There's a time and place for everything, but not now")

"""       
 #A command that is expacted in most bots will show a list of comands to get game rules
@bot.message_handler(commands=['help'])
def help(message):


#output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_resistance'])
def rules_for_resistance(message):
    bot.reply_to(message, "Da Rules (Placeholder)")
"""

#Shows a message with an inline keyboard below it with game options
@bot.message_handler(commands=['new_game'])
def new_game_command_handler(message):
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
#need to be able to end game part way by a majority vote 
@bot.message_handler(commands=['end_game'])
def end_game(message):
  bot.reply_to(message,
"""


#handles the callback from the inline keybaord in the new_game function 
@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games and call.data == "resistance")
def resistance_callback_handler(call):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), types.InlineKeyboardButton(callback_data="start", text="Start Game"))
    bot.edit_message_text("You have selected the game resistance\nTo play resistance we need 5 to 10 people", message_id=call.message.message_id, 
                                                                                                                                                                                    chat_id=call.message.chat.id, 
                                                                                                                                                                                    reply_markup=markup)
    games[call.message.chat.id] = Resistance()


 #built so it should be able to handle the join callback from more then one game
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "join")
def join_callback_handler(call):
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


#built so it should be able to handle the start callback from more then one game
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "start")
def start_callback_handler(call):
    key = call.message.chat.id

    if games[key].game_state == 0:
        if len(games[key].players_id) < games[key].MIN_PLAYERS:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), types.InlineKeyboardButton(callback_data="start", text="Start Game"))
            #this try is here because if the bot trys to edit the message and there is no change it will crash the bot
            try:
                bot.edit_message_text("Not enough players have joined to start the game \nYou need "+str(games[key].MIN_PLAYERS)
                                                    +" to "+str(games[key].MAX_PLAYERS)+" people to play, "+str(len(games[key].players_id))
                                                    +" players have joined", message_id=call.message.message_id, chat_id=key, reply_markup=markup) 
                return
            
            except:
                return

        if len(games[key].players_id) >= games[key].MIN_PLAYERS:
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
                games[key].game_state == 1
                bot.send_message(key, output_message)
                game_round_handler(key)


def game_round_handler(key):
    output_message = games[key].round_setup()
    bot.send_message(key, output_message)
  
    if games[key].game_state == 6:
        del games[key]


@bot.message_handler(commands=['nominate'])
def nominate_command_handler(message):
    key = message.chat.id

    if key not in games:
        bot.reply_to(message, "No game in this chat right now")
        return

    if message.from_user.id == games[key].nominator_id and games[key].game_state == 2:
        output_message = games[key].nominate_logic(message.entities, message.text)
        #nominate_logic will change game_state to 3 if the monimates are valid
        if games[key].game_state == 3:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(callback_data="yea", text="Yea"), types.InlineKeyboardButton(callback_data="nay", text="Nay"))
            bot.reply_to(message, output_message, reply_markup=markup)
        else:
            bot.reply_to(message, output_message)

            
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "nay" or call.message.chat.id in games and call.data == "yea")
def yea_nay_callback_handler(call):
    key = call.message.chat.id
    player_id = call.from_user.id
    
    #I may move this logic to a funtion in the other file
    if player_id in games[key].players_id and player_id not in games[key].players_voted_on_mission and games[key].game_state == 3:
        if call.data == "yea":
            bot.send_message(key, "@" + call.from_user.username + " has voted Yea")
            games[key].mission_yea_votes += 1
        
        if call.data == "nay":
            bot.send_message(key, "@" + call.from_user.username + " has voted Nay")
            games[key].mission_nay_votes += 1
    
        if games[key].mission_nay_votes >= games[key].number_of_players/2:
            bot.send_message(key, "Proposed mission failed to get enough votes")
            game_round_handler(key)
            return
            
        if games[key].mission_yea_votes > games[key].number_of_players/2:
            games[key].game_state = 4
            usernames = ""
            for i in range(len(games[key].players_going_on_mission)):
                usernames += "@" +  games[key].players[games[key].players_going_on_mission[i]].player_username + "\n"  
            bot.send_message(key, usernames + "Are now going on a mission")
        
    

bot.polling()
