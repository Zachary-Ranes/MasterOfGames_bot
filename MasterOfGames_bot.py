#Author: Zachary Ranes
#Written in Python 3.4, requires eternnoir/pyTelegramBotAPI to run

import configparser
import telebot
from telebot import types
from MasterOfGames_bot_Games import Resistance
from MasterOfGames_bot_Games import Mafia

#This loads a config file that holds the bots API key
config = configparser.ConfigParser()
config.read("MasterOfGames_bot_config.cfg")

#The bot object is the go between the telegram API and the python code
bot = telebot.TeleBot(config.get("telegram_bot_api","telegram_token"))

#This dictionary holds the game object that hold all the info about game state, the group chat that the bot is playing the game in is the key
games = {}


#response to the command that is run when the bot is first talked to by user and first added to group-chats 
@bot.message_handler(commands=['start'])
def start_command_handler(message):
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
def help_command_handler(message):
    bot.reply_to(message, "************ HELP ************\n"
                         +"Commands: \n/new_game\n/end_game"
                         +"\nIf you need rules on any of the games you can play with me:\n"
                         +"/rules_resistance"
                         +"/rules_mafia")



#output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_resistance'])
def rules_resistance_command_handler(message):
    bot.reply_to(message, "Da Rules (Placeholder)")



#output text with detailed rules on how to play resistance
@bot.message_handler(commands=['rules_mafia'])
def rules_mafia_command_handler(message):
    bot.reply_to(message, "Da Rules (Placeholder)")



#because sometimes game need to be stopped or reset before the game ends
@bot.message_handler(commands=['end_game'])
def end_game_command_handler(message):
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
def end_continue_callback_handler(call):
    key = call.message.chat.id

    if games[key].game_state == 7:
        if call.data == "continue":
            games[key].pause_game(False)
            bot.edit_message_text("The game will continue",message_id=call.message.message_id, chat_id=call.message.chat.id)
        
        if call.data == "end":
            bot.edit_message_text("The game has been ended!",message_id=call.message.message_id, chat_id=call.message.chat.id)
            del games[key]



#Shows a message with an inline keyboard below it with game options
@bot.message_handler(commands=['new_game'])
def new_game_command_handler(message):
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
def resistance_callback_handler(call):

    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), 
               types.InlineKeyboardButton(callback_data="start", text="Start Game"))

    bot.edit_message_text("You have selected the game resistance\nTo play resistance we need 5 to 10 people", 
                                                                            message_id=call.message.message_id, 
                                                                            chat_id=call.message.chat.id, 
                                                                            reply_markup=markup)
    games[call.message.chat.id] = Resistance()



#handles the callback from the inline keyboard in the new_game function 
@bot.callback_query_handler(func=lambda call: call.message.chat.id not in games and call.data == "mafia")
def resistance_callback_handler(call):

    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), 
               types.InlineKeyboardButton(callback_data="start", text="Start Game"))

    bot.edit_message_text("You have selected the game mafia\nTo play mafia we need 7 or more poeple", 
                                                                            message_id=call.message.message_id, 
                                                                            chat_id=call.message.chat.id, 
                                                                            reply_markup=markup)
    games[call.message.chat.id] = Mafia()
    
    
    
#built so it should be able to handle the join callback from more then one game
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "join")
def join_callback_handler(call):
    key = call.message.chat.id
    
    if games[key].game_state == 0:    
        output_message = games[key].add_player(call.from_user.id, call.from_user.username, call.from_user.first_name)
        
        #add_player will return None if the player has already join the game 
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

                play_round(key)
                
                
#diffrent games have difrent round setup this can handle them all and is call more then once in every game type
def play_round(key):
    if games[key].game_code == 1:
        output_message = games[key].setup_round()
        bot.send_message(key, output_message)
    if games[key].game_code == 2:    
        
        bot.send_message(key,"Mafia")



#handles the nominate command for resistance, nominate_logic can't just be passed message becouse it losses text when passing or atleast apears to 
@bot.message_handler(commands=['nominate'])
def nominate_command_handler(message):
    key = message.chat.id

    if key not in games:
        bot.reply_to(message, "No game in this chat right now")
        return
            
    if message.from_user.id == games[key].nominator_id and games[key].game_state == 2 and games[key].game_code == 1:
        output_message = games[key].nominate_logic(message.entities, message.text)
        #nominate_logic will change game_state to 3 if the nominees are valid
        if games[key].game_state == 3:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(callback_data="yea", text="Yea"), 
                       types.InlineKeyboardButton(callback_data="nay", text="Nay"))
            bot.reply_to(message, output_message, reply_markup=markup)
        else:
            bot.reply_to(message, output_message)
            
            
            
#takes the yea and nay callbacks
#if game state changes it will run the code to setup for a new nominator or it will run code for the mission to start      
@bot.callback_query_handler(lambda call: call.message.chat.id in games and call.data == "nay" 
                                      or call.message.chat.id in games and call.data == "yea")
def yea_nay_callback_handler(call):
    key = call.message.chat.id
    player_id = call.from_user.id
    
    if (games[key].game_state == 3
    and games[key].game_code == 1
    and player_id in games[key].players_id 
    and player_id not in games[key].players_id_voted_on_mission):
    
        output_message = games[key].vote_logic(player_id, call.data)
        bot.send_message(key, output_message)

        if games[key].game_state == 2:
            bot.send_message(key, "Enough votes have been casted, mission will not be preformed")
            play_round(key)
            return
            
        if games[key].game_state == 4:
            output_message = games[key].mission_info(None)
            bot.send_message(key, output_message)
            games[key].setup_mission()
            
            #these two markups add the group chats Id (key) to there callback data so the callback can be associated to the group chat
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
                    bot.send_message(key, "ERROR!!!!\nSome one blocked me since the start of the game, I am sorry the game can not continue")
                    del games[key]
                    
                
                    
#takes the pass fail callbacks from private chats
#informs user of mission result and then starts new round or ends game                   
@bot.callback_query_handler(lambda call: call.data[0:4] == "pass" and int(call.data[4:]) in games 
                                      or call.data[0:4] == "fail" and int(call.data[4:]) in games)
def pass_fail_callback_handler(call):
    key = int(call.data[4:])
    player_id = call.from_user.id
    
    if (games[key].game_state == 4 
    and games[key].game_code == 1
    and player_id in games[key].players_id_going_on_mission 
    and player_id not in games[key].players_id_votes_from_mission):
        
        vote = call.data[0:4]       
        output_message = games[key].mission_logic(player_id, vote)
        
        #this output_message is saying the mission failed or not that is why it is not shown unless the voting is over
        if games[key].game_state != 4:
            bot.send_message(key, output_message)
           
            if games[key].game_state == 2:
                play_round(key)
                
            if games[key].game_state == 5:
                output_message = games[key].who_won()
                bot.send_message(key, output_message)
                del games[key] 


    
bot.polling()
