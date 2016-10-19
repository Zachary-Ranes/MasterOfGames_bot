#Author: Zachary Ranes
#Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

import ConfigParser
import telebot
from telebot import types
from MasterOfGames_bot_Games import Resistance
from MasterOfGames_bot_Games import Mafia

#This loads a config file that holds the bots API key
config = ConfigParser.ConfigParser()
config.read("MasterOfGames_bot_config.cfg")

#The bot object is the go between the telegram API and the python code
bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

#This dictionary holds the game object that hold all the info about game state, the group chat that the bot is playing the game in is the key
games = {}


#response to the command that is run when the bot is first talked to by user and first added to group-chats 
@bot.message_handler(commands=['start'])
def command_start(message):
    if message.chat.type == "private":
        bot.reply_to(message, "Hello, I can now talk with you.\nIf you are not part of a game go to a group chat and run /start")		
        return

    if (message.chat.type == "group" and message.chat.id not in games 
     or message.chat.type == "supergroup" and message.chat.id not in games):
        bot.reply_to(message, "Hello!!! if you would like to play a game type /new_game")
        return
    
    else:
        bot.reply_to(message, "There's a time and place for everything, but not now")


#A command that is expected in most bots will show a list of commands to get game rules
@bot.message_handler(commands=['help'])
def command_help(message):
    bot.reply_to(message, "************ HELP ************\n"
                         +"Commands: \n/new_game\n/end_game"
                         +"\nIf you need rules on any of the games you can play with me:\n"
                         +"/rules_resistance"
                         +"/rules_mafia")


#output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_resistance'])
def command_rules_resistance(message):
    #still need to write the rules
    pass


#output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_mafia'])
def command_rules_mafia(message):
    #still need to write the rules
    pass


#because sometimes game need to be stopped or reset before the game ends
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


#handles the callback from the end_game command 
@bot.callback_query_handler(func=lambda call: call.message.chat.id in games and call.data == "end" 
                                           or call.message.chat.id in games and call.data == "continue")
def callback_end_or_continue(call):
    key = call.message.chat.id

    if games[key].game_state == -1:
        if call.data == "continue":
            games[key].pause_game(False)
            bot.edit_message_text("The game will continue",message_id=call.message.message_id, chat_id=call.message.chat.id)
        
        if call.data == "end":
            bot.edit_message_text("The game has been ended!",message_id=call.message.message_id, chat_id=call.message.chat.id)
            del games[key]


#Shows a message with an inline keyboard below it with game options
@bot.message_handler(commands=['new_game'])
def command_new_game(message):
    if message.chat.type == "private":
        bot.reply_to(message, "You can't make a new game in a private chat")
        return

    if (message.chat.type == "group" and message.chat.id not in games 
     or message.chat.type == "supergroup" and message.chat.id not in games):
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(callback_data="resistance", text="Resistance"),
                   types.InlineKeyboardButton(callback_data="mafia", text="Mafia"))
                   
        bot.send_message(message.chat.id, "Which game would you like to play?", reply_markup=markup)
        return

    else:
        bot.reply_to(message, "There's a time and place for everything, but not now")


#handles the callback from the inline keyboard in the new_game function 
@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games and call.data == "resistance")
def callback_resistance(call):
    key = call.message.chat.id
    games[key] = Resistance()
    
    bot.edit_message_text(games[key].message_for_group[0], 
                          message_id=call.message.message_id, 
                          chat_id=key, 
                          reply_markup=games[key].message_for_group[1])
                          
                          
#handles the callback from the inline keyboard in the new_game function 
@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games and call.data == "mafia")
def callback_mafia(call):
    key = call.message.chat.id
    games[key] = Mafia()
    
    bot.edit_message_text(games[key].message_for_group[0], 
                          message_id=call.message.message_id, 
                          chat_id=key, 
                          reply_markup=games[key].message_for_group[1])

    
#built so it should be able to handle the join callback from more then one game
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "join")
def callback_join(call):
    key = call.message.chat.id
    player_id = call.from_user.id

    if (games[key].game_state == 0 
    and player_id not in games[key].ids_of_players):    

        output_message = games[key].add_player(player_id, call.from_user.username, call.from_user.first_name)
        bot.send_message(key, output_message)
                

#built so it should be able to handle the start callback from more then one game
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "start")
def callback_start(call):
    key = call.message.chat.id

    if games[key].game_state == 0 and call.from_user.id in games[key].ids_of_players    :
        #enough_players will change game state to 1 if there are enough players and return an output if there are not
        games[key].enough_players()
    
        if games[key].game_state == 0:
            #this try is here because if the bot tries to edit the message and there is no change it will crash the bot
            try:
                bot.edit_message_text(games[key].message_for_group[0], 
                                      message_id=call.message.message_id, 
                                      chat_id=key, 
                                      reply_markup=games[key].message_for_group[1]) 
            except:
                pass
                
        if games[key].game_state == 1:
            talk_to_everyone = True

            for i in range(games[key].number_of_players):
                player_id = games[key].ids_of_players[i]
                try:
                    bot.send_message(player_id, "You are part of a group game, don't stop playing mid way please")
                except:
                    bot.send_message(key, "I can not talk to @"+ games[key].players_id_to_username[player_id]
                                        +"\nPlease start a private chat with me, we can not play the game if you do not do so")
                    talk_to_everyone = False
                    games[key].game_state = 0
                        
            #If the bot can not talk to everyone the game can not start        
            if talk_to_everyone:
                games[key].setup_game()
                message_players(key)
                play_game(key)
                

#
def play_game(key):
    games[key].check_for_winner()
    if games[key].game_state == -2:
        bot.send_message(key, games[key].message_for_group[0])
        del games[key] 
    else:
        games[key].setup_round()
        message_players(key)

   
#
def message_players(key):
    if games[key].message_for_group[0] != None:
        bot.send_message(key, games[key].message_for_group[0], reply_markup=games[key].message_for_group[1])

    for player_id in games[key].message_for_players:
        try:
            m = bot.send_message(player_id, games[key].message_for_players[player_id][0], reply_markup=games[key].message_for_players[player_id][1])
            games[key].last_messages[player_id] = m
        except:
            bot.send_message(key, "Someone has blocked me mid way through the game, I am sorry the game can not continue GAME ENDED")
            del games[key]
       
    
#handles the nominate command for resistance, nominate_logic can't just be passed message because it losses text when passing or at least appears to 
@bot.message_handler(commands=['nominate'])
def game1_command_nominate(message):
    key = message.chat.id
    if key in games:
        if message.from_user.id == games[key].id_of_nominator and games[key].game_state == 2 and games[key].game_code == 1:
            games[key].nominate_logic(message.entities, message.text)
            #nominate_logic will change game_state to 3 if the nominees are valid
            bot.reply_to(message, games[key].message_for_group[0], reply_markup=games[key].message_for_group[1])
                
    else:
        bot.reply_to(message, "There's a time and place for everything, but not now")


#takes the yea and nay callbacks
#if game state changes it will run the code to setup for a new nominator or it will run code for the mission to start      
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "nay" 
                                      or call.message.chat.id in games and call.data == "yea")
def game1_callback_yea_or_nay(call):
    key = call.message.chat.id
    player_id = call.from_user.id
    
    if (games[key].game_state == 3
    and games[key].game_code == 1
    and player_id in games[key].ids_of_players 
    and player_id not in games[key].ids_of_players_voted_on_nominees):
    
        output_message = games[key].vote_logic(player_id, call.data)
        bot.send_message(key, output_message)

        if games[key].game_state == 2:
            bot.send_message(key, "Enough nay votes have been casted, mission will not be preformed")
            games[key].setup_round()
            message_players(key)
            
        if games[key].game_state == 4:
            games[key].setup_mission(key)
            message_players(key)
                
            
#takes the pass fail callbacks from private chats
#informs user of mission result and then starts new round or ends game                   
@bot.callback_query_handler(lambda call: call.data[0:4] == "pass" and int(call.data[4:]) in games 
                                      or call.data[0:4] == "fail" and int(call.data[4:]) in games)
def game1_callback_pass_or_fail(call):
    key = int(call.data[4:])
    player_id = call.from_user.id
    
    if (games[key].game_state == 4 
    and games[key].game_code == 1
    and player_id in games[key].ids_of_players_going_on_mission 
    and player_id not in games[key].ids_of_players_voted_from_mission):
        
        vote = call.data[0:4]       
        games[key].mission_logic(player_id, vote)
        
        if games[key].game_state != 4:
            bot.send_message(key, games[key].message_for_group[0])
            play_game(key)
   
#
@bot.callback_query_handler(lambda call: call.data[0:4] == "kill" and int(call.data[6:] in games))
def game2_callback_kill(call):
    key = int(call.data[6:])
    player_id_index = int(call.data[4:6])
    kill_id = games[key].ids_of_players[player_id_index]

    if (games[key].game_state == 2
    and call.from_user.id in games[key].ids_of_players
    and kill_id in games[key].ids_of_players
    and call.from_user.id in games[key].ids_of_mafiosi
    and games[key].role_completed_mafia == False):
        
        kill_vote_logic(kill_id)        
        for player_id in games[key].ids_of_mafiosi:
            try:
                bot.edit_message_text(games[key].message_for_players[player_id][0], 
                                      message_id=games[key].last_messages[player_id].message_id, 
                                      chat_id=player_id1, 
                                      reply_markup=games[key].message_for_players[player_id][1])
            except:
                pass

    if games[key].night_over:
        player_game(key)


#
@bot.callback_query_handler(lambda call: call.data[0:4] == "heal" and int(call.data[6:] in games))
def game2_callback_heal(call):
    key = int(call.data[6:])
    player_id_index = int(call.data[4:6])
    player_id = games[key].ids_of_players[player_id_index]

    if (games[key].game_state == 2
    and player_id in games[key].ids_of_players
    and call.from_user.id in games[key].ids_of_players
    and call.from_user.id == games[key].id_of_doctor 
    and games[key].role_completed_doctor == False):
        
        output_message = games[key].doctor_logic(player_id)
        bot.send_message(call.from_user.id, output_message)

    if games[key].night_over:
        player_game(key)


#
@bot.callback_query_handler(lambda call: call.data[0:4] == "look" and int(call.data[6:] in games))
def game2_callback_look(call):
    key = int(call.data[6:])
    player_id_index = int(call.data[4:6])
    player_id = games[key].ids_of_players[player_id_index]

    if (games[key].game_state == 2
    and player_id in games[key].ids_of_players
    and call.from_user.id in games[key].ids_of_players
    and call.from_user.id == games[key].id_of_detective
    and games[key].role_completed_detective == False):
        
        roll_info = games[key].detective_logic(player_id)
        bot.send_message(call.from_user.id, roll_info)

    if games[key].night_over:
        player_game(key)


#
@bot.callback_query_handler(lambda call: call.data[0:4] == "hang" and int(call.data[6:] in games))
def game2_callback_hang(call):
    key = int(call.data[6:])
    player_id_index = int(call.data[4:6])
    player_id = games[key].ids_of_players[player_id_index]

    if (games[key].game_state == 3
    and player_id in games[key].ids_of_players
    and call.from_user.id in games[key].ids_of_players):

        output_message = games[key].lych_nominate_logic(player_id)
        bot.send_message(key, output_message)

        if game_state == 4:
            message_players(key)
    

#
@bot.callback_query_handler(lambda call: call.data[0:4] == "vote" and int(call.data[6:] in games))
def game2_callback_vote(call):
    key = int(call.data[6:])
    player_id_index = int(call.data[4:6])
    player_id = games[key].ids_of_players[player_id_index]

    if (games[key].game_state == 4
    and player_id in games[key].ids_of_players
    and call.from_user.id in games[key].ids_of_players):

        games[key].lynch_vote_logic(player_id)

        if games[key].game_state != 4:
            message_players(key)

            if games[key].game_state == 2:
                play_game(key)



bot.polling()
