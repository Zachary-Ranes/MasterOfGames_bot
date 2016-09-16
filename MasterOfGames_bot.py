#Written by Zachary Ranes
#Written for Python 3.4

import configparser
import telebot
from telebot import types
from MasterOfGames_bot_Games import Resistance

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
    markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), 
                      types.InlineKeyboardButton(callback_data="start", text="Start Game"))
    bot.edit_message_text("You have selected the game resistance\nTo play resistance we need 5 to 10 people", message_id=call.message.message_id, 
                                                                                                                                                                                    chat_id=call.message.chat.id, 
                                                                                                                                                                                    reply_markup=markup)
    games[call.message.chat.id] = Resistance()


    
 #built so it should be able to handle the join callback from more then one game
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "join")
def join_callback_handler(call):
    key = call.message.chat.id
    
    if games[key].game_state == 0:    
        output_message = games[key].add_player(call.from_user.id, call.from_user.username, call.from_user.first_name)
    
        if output_message != None:
            bot.send_message(key, output_message)
        
        

#built so it should be able to handle the start callback from more then one game
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "start")
def start_callback_handler(call):
    key = call.message.chat.id
    player_id = call.from_user.id

    if games[key].game_state == 0 and player_id in games[key].players_id:
        output_message = games[key].setup_game()
    
        if games[key].game_state == 0:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), 
                              types.InlineKeyboardButton(callback_data="start", text="Start Game"))
           #this try is here because if the bot trys to edit the message and there is no change it will crash the bot
            try:
                bot.edit_message_text(output_message, message_id=call.message.message_id, chat_id=key, reply_markup=markup) 
                return
                
            except:
                return

        if games[key].game_state == 1:
            talk_to_everyone = True

            for i in range(games[key].number_of_players):
                player_id = games[key].players_id[i]
                try:
                    bot.send_message(player_id, games[key].player_roll_info(player_id))
                except:
                    bot.send_message(key, "I can not talk to @"+ games[key].player_ids_to_username[player_id]
                                                     +"\nPlease start a private chat with me, we can not play the game if you do not do so")
                    talk_to_everyone = False
                    games[key].game_state = 0

            #If the bot can not talk to everyone the game can not start        
            if talk_to_everyone:		
                bot.send_message(key, output_message)
                
                output_message = games[key].setup_round()
                bot.send_message(key, output_message)



#
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
            markup.row(types.InlineKeyboardButton(callback_data="yea", text="Yea"), 
                              types.InlineKeyboardButton(callback_data="nay", text="Nay"))
            bot.reply_to(message, output_message, reply_markup=markup)
        else:
            bot.reply_to(message, output_message)

            
            
#       
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "nay" 
                                                           or call.message.chat.id in games and call.data == "yea")
def yea_nay_callback_handler(call):
    key = call.message.chat.id
    player_id = call.from_user.id
    
    if player_id in games[key].players_id and player_id not in games[key].players_id_voted_on_mission and games[key].game_state == 3:
        output_message1, output_message2 = games[key].vote_logic(player_id, call.data)
        
        bot.send_message(key, output_message2)

        if games[key].game_state == 2:
            bot.send_message(key, output_message1)
            output_message = games[key].setup_round()
            bot.send_message(key, output_message)
            return
    
        if games[key].game_state == 4:
            bot.send_message(key, output_message1)
            games[key].setup_mission()
            
            markup_resistance = types.InlineKeyboardMarkup()
            markup_resistance.row(types.InlineKeyboardButton(callback_data="pass"+str(key), text="Pass"))
            
            markup_spys = types.InlineKeyboardMarkup()
            markup_spys.row(types.InlineKeyboardButton(callback_data="pass"+str(key), text="Pass"), 
                                         types.InlineKeyboardButton(callback_data="fail"+str(key), text="Fail"))
        
            for i in range(len(games[key].players_id_going_on_mission)):
                player_id = games[key].players_id_going_on_mission[i]
                
                if player_id in games[key].spys_id:
                    markup = markup_spys
                else:
                    markup = markup_resistance
                
                try:
                    output_message = games[key].mission_info(player_id)
                    bot.send_message(player_id, output_message, reply_markup=markup)
                except:
                    #I do not know what the bot should do if someone blocks it part of the way through the game........
                    bot.send_message(key, "ERROR!!!!")

                    
                    
#                    
@bot.callback_query_handler(lambda call: call.data[0:4] == "pass" and call.data[4:] in games or call.data[0:4] == "fail" and call.data[4:] in games)
def pass_fail_callback_handler(call):
    key = call.data[4:]
    player_id = call.from_user.id
    
    if (games[key].game_state == 4
        and player_id in games[key].players_id_going_on_mission 
        and player_id not in games[key].players_voted_on_mission):
        
        output_message1, output_message2 = games[key].mission_logic(player_id, call.data[0:4])

        if games[key].game_state != 4:
            bot.send_message(key, output_message1)
            
            if games[key].game_state == 2:
                output_message = games[key].setup_round()
                bot.send_message(key, output_message)
            
            if games[key].game_state == 5:
                bot.send_message(key, output_message2)
                del games[key] 

    
    
    
bot.polling()
