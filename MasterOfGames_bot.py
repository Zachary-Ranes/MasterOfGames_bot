#Author: Zachary Ranes
#Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

import ConfigParser

#import for the Python Telegram bot API 
import telebot
from telebot import types

#import the games logic 
from MasterOfGames_bot_Games import Resistance
from MasterOfGames_bot_Games import Mafia

#This loads a configure file that holds the bots API key
config = ConfigParser.ConfigParser()
config.read("Config.cfg")

#The bot object is the go between the telegram API and the python code
bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

#This dictionary holds the game objects which are the instances of the games
#key : the id of the chat the game object belongs to, no duplicate keys  
games = {}

#Start is run when a bot when the bot is added to a chat or first private messaged
@bot.message_handler(commands=['start'])
def command_start(message):
    if message.chat.type == "private":
        bot.reply_to(message, "Hello, I can now talk with you.\nIf this is your first time talking"\
                              " to me and you would like to play a game with me add me to a group"\
                              " and run /start")		

    if (message.chat.type == "group" and message.chat.id not in games 
     or message.chat.type == "supergroup" and message.chat.id not in games):
        bot.reply_to(message, "Hello!!! if you would like to play a game type /new_game")

#A command that is expected in most bots, will show a list of commands to get game rules
@bot.message_handler(commands=['help'])
def command_help(message):
    bot.reply_to(message, "To start a new game run /new_game if you need to end a game before it "\
                          "has has gotten to its end run /end_game also if you need rules for how "\
                          "to play a game the flowing rule books are available (run theses in a "\
                          "private chat because they are long) /rules_resistance /rules_mafia")

#Output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_resistance'])
def command_rules_resistance(message):
    with open("Rules_resistance.txt", "rb") as rules_resistance:
        bot.reply_to(message, rules_resistance.read())

#Output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_mafia'])
def command_rules_mafia(message):
    with open("Rules_mafia.txt", "rb") as rules_mafia:
        bot.reply_to(message, rules_mafia.read())

#Provides the ability for players to end a game before it is played fully 
@bot.message_handler(commands=['end_game'])
def command_end_game(message):
    key = message.chat.id

    if key in games:
        games[key].pause_game(True)

        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="end", text="End Game"),
                   types.InlineKeyboardButton(callback_data="continue", text="Continue"))                
        bot.reply_to(message, "Are you sure you want to end the game?!", reply_markup=markup) 
    else:
        bot.reply_to(message, "There's a time and place for everything, but not now")

#Handles the callback from the end_game command 
@bot.callback_query_handler(func=lambda call: call.message.chat.id in games 
                                              and call.data == "end" 
                                           or call.message.chat.id in games 
                                              and call.data == "continue")
def callback_from_end_game(call):
    key = call.message.chat.id

    if games[key].game_state == -1:
        if call.data == "continue":
            games[key].pause_game(False)
            bot.edit_message_text("The game will continue", 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id)
        if call.data == "end":
            bot.edit_message_text("The game has been ended!", 
                                  message_id=call.message.message_id, 
                                  chat_id=call.message.chat.id)
            del games[key]
    else:
        pass

#Responds to players request for a new game and shows what games can be played
@bot.message_handler(commands=['new_game'])
def command_new_game(message):
    key = message.chat.id

    if message.chat.type == "private":
        bot.reply_to(message, "You can't make a new game in a private chat")

    if (message.chat.type == "group" and key not in games 
     or message.chat.type == "supergroup" and key not in games):
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="resistance", text="Resistance"),
                   types.InlineKeyboardButton(callback_data="mafia", text="Mafia"))
        bot.send_message(key, "Which game would you like to play?", reply_markup=markup)
    else:
        bot.reply_to(message, "There's a time and place for everything, but not now")

#Handles the callback from new_game and adds an instance of the proper game to the games dictionary  
@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games 
                                              and call.data == "resistance"
                                           or call.message.chat.id not in games 
                                              and call.data == "mafia")
def callback_from_new_game(call):
    key = call.message.chat.id
    
    if call.data == "resistance":
        games[key] = Resistance()
    if call.data == "mafia":
        games[key] = Mafia()

    bot.edit_message_text(games[key].message_for_group[0], 
                          message_id=call.message.message_id, 
                          chat_id=key, 
                          reply_markup=games[key].message_for_group[1])
                              
#Handles join callback adding player to the active game or shows why the player can not be added
@bot.callback_query_handler(lambda call: call.message.chat.id in games 
                                         and call.data == "join")
def callback_join(call):
    add_player_message = games[call.message.chat.id].add_player(call.from_user.id, 
                                                                call.from_user.username, 
                                                                call.from_user.first_name)
    if add_player_message:
        bot.send_message(call.message.chat.id, add_player_message)
                
#Handles start callback, check to see if the game can start and if it can starts the game
@bot.callback_query_handler(lambda call: call.message.chat.id in games 
                                         and call.data == "start")
def callback_start(call):
    key = call.message.chat.id

    if games[key].can_start_game(call.from_user.id):
        talked_to_everyone = True
        for player_id in games[key].ids_of_players:
            try:
                bot.send_message(player_id, "Checking if I can talk to you")
            except:
                bot.send_message(key, "I can not talk to @"
                                     + games[key].players_id_to_username[player_id]
                                     +"\nPlease start a private chat with me, "\
                                      "we can not play the game if you do not do so")
                games[key].can_start_game("false_start")
                talked_to_everyone = False
        if talked_to_everyone:
            games[key].setup_game(key)
            message_players(key)
            play_round(key)
    else:
        try:
            bot.edit_message_text(games[key].message_for_group[0], 
                                  message_id=call.message.message_id, 
                                  chat_id=key, 
                                  reply_markup=games[key].message_for_group[1]) 
        #The API will throw an error if you try to edit a message and the edit is not different
        #That is why this except does nothing just prevents the bot from crashing       
        except: pass
               
#Called when a new round in ether game starts
def play_round(key):
    if games[key].win_state():
        bot.send_message(key, games[key].message_for_group[0])
        del games[key] 
    else:
        games[key].setup_round()
        message_players(key)

#Sends private messages to all player there is a message for and to the group 
#Will delete the game object if the bot can no long talk to a player
def message_players(key):
    if games[key].message_for_group[0] != None:
        bot.send_message(key, 
                         games[key].message_for_group[0], 
                         reply_markup=games[key].message_for_group[1])
    for player_id in games[key].message_for_players:
        try:
            message = (bot.send_message(player_id, 
                                        games[key].message_for_players[player_id][0], 
                                        reply_markup=games[key].message_for_players[player_id][1]))
            games[key].last_messages[player_id] = message
        #Last messages are stored so there ids can be checked so they can be edited later 
        except:
            bot.send_message(key, "Someone has blocked me mid way through the game, "\
                                  "I am sorry the game can not continue GAME ENDED")
            del games[key]
           
#Handles the nominate command used in the resistance game
@bot.message_handler(commands=['nominate'])
def resistance_command_nominate(message):
    key = message.chat.id
    if key in games:
        if games[key].game_type("resistance"):  
            if games[key].nominate_logic(message.from_user, message.entities, message.text):
                bot.reply_to(message, 
                             games[key].message_for_group[0], 
                             reply_markup=games[key].message_for_group[1])
        else:
            bot.reply_to(message, "There's a time and place for everything, but not now")

#Handles the callback which is a vote on the nomination  
@bot.callback_query_handler(lambda call: call.message.chat.id in games 
                                         and call.data == "nay" 
                                      or call.message.chat.id in games 
                                         and call.data == "yea")
def resistance_callback_from_nomination(call):
    key = call.message.chat.id
    if games[key].game_type("resistance"):
        logic_output = games[key].nomination_vote_logic(call.from_user.id, call.data)
        if logic_output:
            try:
                bot.edit_message_text(games[key].message_for_group[0], 
                                      message_id=call.message.message_id, 
                                      chat_id=key, 
                                      reply_markup=games[key].message_for_group[1]) 
            except: pass
        if logic_output == "Fail":
            games[key].setup_round()
            message_players(key)
        if logic_output == "Pass":
            games[key].setup_mission(key)
            message_players(key)
                            
#takes the pass fail callbacks from private chats
#informs user of mission result and then starts new round or ends game                   
@bot.callback_query_handler(lambda call: call.data[0:4] == "pass" 
                                         and int(call.data[4:]) in games 
                                      or call.data[0:4] == "fail" 
                                         and int(call.data[4:]) in games)
def resistance_callbacks_from_mission(call):
    key = int(call.data[4:])
    if games[key].game_type("resistance"):
        if games[key].mission_logic(call.from_user.id, call.data[0:4]):
            bot.send_message(key, games[key].message_for_group[0])
            play_round(key)
   
#The callback handler for a mafia player targeting a player to kill
@bot.callback_query_handler(lambda call: call.data[0:4] == "kill" 
                                         and int(call.data[6:]) in games)
def mafia_callback_kill(call):
    key = int(call.data[6:])
    killer_id = call.from_user.id
    target_player_id_index = int(call.data[4:6])
    target_player_id = games[key].ids_of_innocents[target_player_id_index]

    if games[key].game_type("mafia"):
        if games[key].kill_vote_logic(killer_id, target_player_id):
            for player_id in games[key].message_for_players:
                try:
                    bot.edit_message_text(games[key].message_for_players[player_id][0], 
                                          message_id=games[key].last_messages[player_id].message_id, 
                                          chat_id=player_id, 
                                          reply_markup=games[key].message_for_players[player_id][1])
                except: pass
            if games[key].night_over():
                player_game(key)

#The callback handler for the doctor choosing who to heal 
@bot.callback_query_handler(lambda call: call.data[0:4] == "heal" 
                                         and int(call.data[6:]) in games)
def mafia_callback_heal(call):
    key = int(call.data[6:])
    player_id = call.from_user.id
    target_player_id_index = int(call.data[4:6])
    target_player_id = games[key].ids_of_players[target_player_id_index]

    if games[key].game_type("mafia"):
        logic_output = games[key].doctor_logic(player_id, target_player_id)
        if logic_output:
            bot.send_message(player_id, logic_output)

            if games[key].night_over():
                player_game(key)

#The callback handler for the detective checking a player role 
@bot.callback_query_handler(lambda call: call.data[0:4] == "look" 
                                         and int(call.data[6:]) in games)
def mafia_callback_look(call):
    key = int(call.data[6:])
    player_id = call.from_user.id
    target_player_id_index = int(call.data[4:6])
    target_player_id = games[key].ids_of_players[target_player_id_index]

    if games[key].game_type("mafia"):
        logic_output = games[key].detective_logic(player_id, target_player_id)
        if logic_output:
            bot.send_message(player_id, logic_output)

            if games[key].night_over():
                player_game(key)

#The callback handler for the group voting on who to lynch
@bot.callback_query_handler(lambda call: call.data[0:5] == "lynch"
                                         and call.message.chat.id in games)
def mafia_callback_lych(call):
    key = call.message.chat.id
    player_id = call.from_user.id
    target_player_id = call.data[5:0]

    if games[key].game_type("mafia"):
        logic_output = games[key].lynch_logic(player_id, target_player_id)
        
        if logic_output:
            try:
                bot.edit_message_text(games[key].message_for_group[0],
                                      message_id=call.message.message_id,
                                      chat_id=call.message.chat.id,
                                      reply_markup=games[key].message_for_group[1])
            except: pass

            if logic_output in games[key].ids_of_players:
                bot.send_message(key, "@"+ games[key].players_id_to_username[logic_output] 
                                         +" has been lynched, this dark day is done.")
                play_round(key)
    

bot.polling()
