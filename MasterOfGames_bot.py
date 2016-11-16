#Author: Zachary Ranes
#Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

import ConfigParser
import telebot
from telebot import types
from Game_Resistance import Resistance
from Game_Mafia import Mafia

#This loads a configure file that holds the bots API key
config = ConfigParser.ConfigParser()
config.read("Config.cfg")
#The bot object is the go between the telegram API and the python code
bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))
#This dictionary holds the game objects which are the instances of the games
#key : the id of the chat the game object belongs to, no duplicate keys  
games = {}

#Start is run when a bot is added to a chat or first private messaged
@bot.message_handler(commands=['start'])
def command_start(message):
    if message.chat.type == "private":
        bot.reply_to(message, "Hello, I can now talk with you.\nIf this is "\
                              "your first time talking to me and you would "\
                              "like to play a game with me add me to a group"\
                              " and run /start")      
    if (message.chat.type == "group" and message.chat.id not in games 
    or message.chat.type == "supergroup" and message.chat.id not in games):
        bot.reply_to(message, "Hello!!! if you would like to play a game "\
                              "type /new_game")

#A command that is expected in most bots
@bot.message_handler(commands=['help'])
def command_help(message):
    bot.reply_to(message, "To start a new game run /new_game if you need to "\
                          "end a game before it has has gotten to its end run "\
                          "/end_game also if you need rules for how to play a "\
                          "game the flowing rule books are available:\n "\
                          "/rules_resistance \n/rules_mafia")

#Output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_resistance'])
def command_rules_resistance(message):
    with open("Rules_resistance.txt", "rb") as rules:
        bot.reply_to(message, rules.read())

#Output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_mafia'])
def command_rules_mafia(message):
    with open("Rules_mafia.txt", "rb") as rules:
        bot.reply_to(message, rules.read())

#Responds to players request for a new game and shows what games can be played
@bot.message_handler(commands=['new_game'])
def command_new_game(message):
    key = message.chat.id
    if (message.chat.type == "group" and key not in games 
    or message.chat.type == "supergroup" and key not in games):
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="MoG_resistance", 
                                              text="Resistance"),
                   types.InlineKeyboardButton(callback_data="MoG_mafia", 
                                              text="Mafia"))
        bot.send_message(key, 
                         "Which game would you like to play?", 
                         reply_markup=markup)
    else:
        bot.reply_to(message, 
                    "There's a time and place for everything, but not now")

#Handles the callback from new_game and adds an instance to games
@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games 
                                              and call.data == "MoG_resistance"
                                           or call.message.chat.id not in games 
                                              and call.data == "MoG_mafia")
def callbacks_from_new_game(call):
    key = call.message.chat.id
    if call.data == "MoG_resistance":
        games[key] = Resistance(key)
    if call.data == "MoG_mafia":
        games[key] = Mafia(key)
    output = games[key].setup_pregame()
    bot.edit_message_text(output[0], 
                          message_id=call.message.message_id, 
                          chat_id=key, 
                          reply_markup=output[1])
                              
#Handles join callback adding player to the active game or shows error
@bot.callback_query_handler(lambda call: call.message.chat.id in games 
                                         and call.data == "MoG_join")
def callback_join(call):
    key = call.message.chat.id
    #returns false if user has already joined 
    output = games[key].add_player(call.from_user.id, 
                                   call.from_user.username, 
                                   call.from_user.first_name)
    if output:
        bot.edit_message_text(output[0], 
                              message_id=call.message.message_id, 
                              chat_id=key, 
                              reply_markup=output[1])
              
#Handles start callback, check to see if the game can start 
@bot.callback_query_handler(lambda call: call.message.chat.id in games 
                                         and call.data == "Mog_start")
def callback_start(call):
    key = call.message.chat.id
    if games[key].can_game_start(call.from_user.id):
        error = check_privilege(key)
        if error:
            bot.send_message(key, error)
        else:
            bot.edit_message_text("Game of "+ games[key].game_name +" started", 
                                  message_id=call.message.message_id, 
                                  chat_id=key,
                                  reply_markup=None)
            games[key].setup_game()
            new_round()

#Sends a test message to all players returns error if can not talk to someone
def check_privilege(key):
    talk_to_everyone = True
    error_message = "I can not talk to the following player(s)" 
    for player_id in games[key].players_id_to_username:
        try:
            bot.send_message(player_id, "Checking that I can talk with you")
        except:
            error_message += " @" + games[key].players_id_to_username[player_id]  
            talk_to_everyone = False

    if talk_to_everyone:
        return False
    else:
        error_message += "\nPlease start a private chat with me, we can not "\
                         "start playing the game till these players do."
    #game_state 0 is looking for plays to join or hit start 
    games[key].game_state = 0
    return error_message

#Sends private messages to all player there is a message for and to the group
def message_all(key):
    if games[key].message_for_group:
        bot.send_message(key, 
                         games[key].message_for_group[0], 
                         reply_markup=games[key].message_for_group[1])
    for player_id in games[key].message_for_players:
        try:
            message_sent = (bot.send_message(\
                player_id, 
                games[key].message_for_players[player_id][0], 
                reply_markup=games[key].message_for_players[player_id][1]))
            games[key].last_messages_ids[player_id] = message_sent.message_id
    #Possible upgrade later make a wait of some kind here and give the person
    #A chance to start the chat with the bot again and not just end the game
        except:
            bot.send_message(key, "Someone has blocked me mid way through "\
                                  "the game, I am sorry the game can not "\
                                  "continue GAME TERMMINADED")
            del games[key]

#
def new_round():
    message_all(key)
    game_over = games[key].end_state()
    if game_over:
        bot.send_message(key, game_over)    
        del games[key]
    else:
        games[key].setup_round()
        message_all(key)
           
#Handles the nominate command used in the resistance game
@bot.message_handler(commands=['nominate'])
def resistance_command_nominate(message):
    key = message.chat.id
    if key in games:
        if games[key].game_name == "resistance":  
            output = games[key].nominate_logic(message.from_user.id, 
                                               message.entities, 
                                               message.text)
            bot.reply_to(message, output[0], reply_markup=output[1])

#Handles the callback which is a vote on the nomination  
@bot.callback_query_handler(lambda call: call.message.chat.id in games 
                                         and call.data == "MoG_nominate_nay" 
                                         or call.message.chat.id in games 
                                         and call.data == "MoG_nominate_yea")
def resistance_callbacks_from_nomination(call):
    key = call.message.chat.id
    if games[key].game_name == "resistance": 
        output = games[key].nomination_vote_logic(call.from_user.id, call.data)
        if output:
            bot.send_message(key, output)
            #nomination_successful returns None if more votes are needed
            if games[key].game_state == 4:
                bot.edit_message_text(games[key].message_for_group[0], 
                                      message_id=call.message.message_id, 
                                      chat_id=key,
                                      reply_markup=None)
                games[key].setup_mission()
                message_all(key)
            if games[key].game_state == 2:
                bot.edit_message_text(games[key].message_for_group[0], 
                                      message_id=call.message.message_id, 
                                      chat_id=key,
                                      reply_markup=None)
                games[key].setup_round()
                message_all(key)

#takes the pass fail callbacks from private chats
#informs user of mission result and then starts new round or ends game                   
@bot.callback_query_handler(lambda call: call.data[0:16]== "MoG_mission_pass" 
                                         and int(call.data[16:]) in games 
                                         or call.data[0:16]== "MoG_mission_fail" 
                                         and int(call.data[16:]) in games)
def resistance_callbacks_from_mission(call):
    key = int(call.data[16:])
    if games[key].game_name == "resistance":
        output = games[key].mission_logic(call.from_user.id, call.data[0:16])
        if output:
            try:
                bot.edit_message_text(output,
                                      message_id=call.message.message_id,
                                      chat_id=player_id,
                                      reply_markup=None)
            except: pass
            if games[key].game_state == 5:
                new_round()

#The callback handler for a mafia player targeting a player to kill
@bot.callback_query_handler(lambda call: call.data[0:14] == "MoG_night_kill" 
                                         and int(call.data[16:]) in games)
def mafia_callback_kill(call):
    key = int(call.data[16:])
    killer_id = call.from_user.id
    target_player_id_index = int(call.data[14:16])
    target_player_id = games[key].ids_of_players[target_player_id_index]
    if games[key].game_name == "mafia": 
        output = games[key].mafia_logic(killer_id, target_player_id)
        for player_id in output:
            try:
                bot.edit_message_text(output[player_id][0], 
                    message_id=games[key].last_messages_ids[player_id], 
                    chat_id=player_id, 
                    reply_markup=output[player_id][1])
            except: pass
        if games[key].night_over():
            new_round()

#The callback handler for the doctor choosing who to heal 
@bot.callback_query_handler(lambda call: call.data[0:14] == "MoG_night_heal" 
                                         and int(call.data[16:]) in games)
def mafia_callback_heal(call):
    key = int(call.data[16:])
    healer_id = call.from_user.id
    target_player_id_index = int(call.data[14:16])
    target_player_id = games[key].ids_of_players[target_player_id_index]
    if games[key].game_name == "mafia": 
        output = games[key].doctor_logic(healer_id, target_player_id)
        if output:
            try:
                bot.edit_message_text(output[0],
                                      message_id=call.message.message_id,
                                      chat_id=player_id,
                                      reply_markup=output[1])
            except: pass
            if games[key].night_over():
                new_round()

#The callback handler for the detective checking a player role 
@bot.callback_query_handler(lambda call: call.data[0:14] == "MoG_night_look" 
                                         and int(call.data[16:]) in games)
def mafia_callback_look(call):
    key = int(call.data[16:])
    looker_id = call.from_user.id
    target_player_id_index = int(call.data[14:16])
    target_player_id = games[key].ids_of_players[target_player_id_index]
    if games[key].game_name == "mafia": 
        output = games[key].detective_logic(looker_id, target_player_id)
        if output:
            try:
                bot.edit_message_text(output[0],
                                      message_id=call.message.message_id,
                                      chat_id=player_id,
                                      reply_markup=output[1])
            except: pass
            if games[key].night_over():
                new_round()

#The callback handler for the group voting on who to lynch
@bot.callback_query_handler(lambda call: call.data[0:13] == "MoG_day_lynch"
                                         and call.message.chat.id in games)
def mafia_callback_lych(call):
    key = call.message.chat.id
    player_id = call.from_user.id
    target_player_id = call.data[13:]
    if games[key].game_name == "mafia": 
        output = games[key].lynch_logic(player_id, target_player_id)
        if output:
            try:
                bot.edit_message_text(output[0],
                                      message_id=call.message.message_id,
                                      chat_id=call.message.chat.id,
                                      reply_markup=output[1])
            except: pass
            if games[key].day_over():
                new_round()



bot.polling()
