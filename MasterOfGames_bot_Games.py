    #Author: Zachary Ranes
    #Written in Python 2.7, requires eternnoir/pyTelegramBotAPI to run

    import math
    from random import shuffle

    import telebot
    from telebot import types

    #The base class that all the game types inherit from 
    class Game(object):
        
        #Constructor for class 
        def __init__(self, game_code = None, min_players = None, max_players = None):
            #Each game has its own code 
            #Resistance: 1
            #Mafia: 2
            self.game_code = game_code
            
            self.MIN_PLAYERS = min_players
            self.MAX_PLAYERS = max_players
            
            #The game state is check to see what functions can be run
            self.game_state = 0
            self.game_state_before_pause = None
            
            self.ids_of_players = []
            self.number_of_players = 0
        
            self.players_id_to_username = {}
            self.players_username_to_id = {}
            
            #This markup is used by all games to have players join the game
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(callback_data="join", text="Join"), 
                       types.InlineKeyboardButton(callback_data="start", text="Start Game"))
            #The string part is black because it is assigned in the children classes 
            self.message_for_group = ["", markup]
            #format {key:["", markup], key:["", markup]}
            self.message_for_players = {}
            self.last_messages = {}
            
        #Returns a message saying the user has been added to the game or an error message
        def add_player(self, player_id, player_username, player_name):
            if player_username == None:
                return "I am sorry "+ player_name +" but you must have an @UserName to play"
            
            if len(self.ids_of_players) >= self.MAX_PLAYERS:
                return "I am sorry @"+ player_username +" but we already have the max number of player for this game"
           
            else: 
                self.ids_of_players.append(player_id)
                self.players_id_to_username[player_id] = player_username
                self.players_username_to_id[player_username] = player_id
                return "@"+ player_username +" has joined the game"
        
        #If there are enough player changes game_state to 1 if there is not changes the group message
        def enough_players(self):
            self.number_of_players = len(self.ids_of_players)
            
            if self.number_of_players < self.MIN_PLAYERS:
                self.message_for_group[0] = ("Not enough players have joined to start the game.\n"\
                                             "You need "+str(self.MIN_PLAYERS)+" to "\
                                             +str(self.MAX_PLAYERS)+" people to play, "\
                                             +str(self.number_of_players) +" players have joined")
            else:
                self.game_state = 1
            
        #Function is different for each game but needed in all games
        def setup_game(self):
            pass
              
        #Function is different for each game but needed in all games
        def setup_round(self, key):
            pass

        #Function is different for each game but needed in all games
        def check_for_winner(self):
            pass
                
        #If given true will pause game and store passed state if given false will restore passed state
        def pause_game(self, value):
            if value == True:
                self.game_state_before_pause = self.game_state
                self.game_state = -1
            if value == False:
                self.game_state = self.game_state_before_pause
                self.game_state_before_pause = None
                
        #Returns a string of usernames from the given list excluding any in the other list
        def list_usernames(self, list_of_excluded_id, list_of_player_ids):
            output = ""
            for player_id in list_of_player_ids:
                if player_id not in list_of_excluded_id:
                    output += " @" + self.players_id_to_username[player_id]
            return output
        
            
    #An object of this class holds all the logic to play Resistance     
    class Resistance(Game):

        #Constructor for class 
        def __init__(self, game_code = 1, min_players = 5, max_players = 10):
            super(Resistance, self).__init__(game_code, min_players, max_players)
            
            """
            game_state is set to 0 in the parent class constructor
            
            game_state = 0 : game has not start (players can still join)
            game_state = 1 : the game has started (players cant hit join)
            game_state = 2 : looking for nominees for a mission
            game_state = 3 : looking for votes on nominees for mission
            game_state = 4 : voting over, players going on mission
            game_state = -2 : game has ending one team has scored 3 points
            game_state = -1 = game is paused (waiting for the game to be ended or continued)
            """

            #First message to group this variable will be used to hold that will be sent to the group
            self.message_for_group[0] = "You have selected the game resistance.\n"\
                                        "To play resistance we need 5 to 10 people."
            
            #The 3d array made here will find the nominees that will be need per round 
            self.FIVE_PLAYERS = [2,3,2,3,3]
            self.SIX_PLAYERS = [2,3,4,3,4]
            self.SEVEN_PLAYERS = [2,3,3,4,4]
            self.EIGHT_PLUS_PLAYERS = [3,4,4,5,5]
            self.PLAYERS_PER_ROUND = [self.FIVE_PLAYERS, 
                                      self.SIX_PLAYERS, 
                                      self.SEVEN_PLAYERS, 
                                      self.EIGHT_PLUS_PLAYERS, 
                                      self.EIGHT_PLUS_PLAYERS, 
                                      self.EIGHT_PLUS_PLAYERS]

            self.game_round = 0
                    
            self.ids_of_resistances = []
            self.ids_of_spies = []
            self.number_of_spies = 0
            
            self.id_of_nominator = None
            self.last_nominator_index = 0
            
            self.number_of_nominees = None
            self.two_fail_mission = False
            
            self.ids_of_players_going_on_mission = []

            self.ids_of_players_voted_on_nominees = []
            self.nominees_yea_votes = 0
            self.nominees_nay_votes = 0
            
            self.ids_of_players_voted_from_mission = []
            self.mission_fail_votes = 0
            self.mission_pass_votes = 0
            
            self.points_spies = 0
            self.points_resistance = 0
        
        #Method is called once after all players have joined 
        def setup_game(self):
            self.number_of_spies = int(math.ceil(self.number_of_players/3))
            #shuffling user IDs so the roles are not determined by what order people joined the game
            shuffle(self.ids_of_players)

            for i in range(self.number_of_spies):
                self.ids_of_spies.append(self.ids_of_players[i])
            
            for player_id in self.ids_of_players:
                if player_id not in self.ids_of_spies:
                    self.ids_of_resistances.append(player_id)
                    
            self.message_for_group[0] = "The game of Resistance has started! \nThere are "\
                                         + str(self.number_of_spies) +" spies in the game."
            self.message_for_group[1] = None
            
            for player_id in self.ids_of_resistances:
                self.message_for_players[player_id] = ("You are part of the Resistance\n"\
                                                       "You win when 3 missions succeed", None)
                
            for player_id in self.ids_of_spies:
                self.message_for_players[player_id] = ("You are a Spy\n You win when 3 missions fail\n"\
                                                       "The other spies are:"
                                                       +self.list_usernames([player_id], \
                                                                            self.ids_of_spies), None)

            #shuffled again so turn order does not give away roles
            shuffle(self.ids_of_players)
            self.game_state = 2
     
        #Method called at the start of every round of the game
        def setup_round(self, key):
            self.id_of_nominator = self.ids_of_players[self.last_nominator_index]   
            self.last_nominator_index += 1
            if self.last_nominator_index == self.number_of_players:
                self.last_nominator_index == 0
            
            #Game setup rule certain mission will need two fail votes from spies to fail
            if self.game_round == 3 and self.number_of_players >= 7:
                self.two_fail_mission = True
                extra_message = "This round requires two spies to vote for failure to fail\n"
            else:
                self.two_fail_mission = False
                extra_message = ""

            self.number_of_nominees = self.PLAYERS_PER_ROUND[self.number_of_players-self.MIN_PLAYERS]\
                                                            [self.game_round]
            self.message_for_group[0] = ("@"+ self.players_id_to_username[self.id_of_nominator] 
                                     +" gets to nominate "+ str(self.number_of_nominees) 
                                     +" players to go on the mission\n"+ extra_message
                                     +"Nominate players by typing /nominate (space) @username "
                                     +"(space) @username ...etc")
            self.message_for_group[1] = None
            self.message_for_players = {}
        
        #Method will change group message and game_state if a victory state is reached
        def check_for_winner(self):
            if self.points_resistance >= 3:
                self.game_state = -2
                self.message_for_group[0] = "The resistance has scored 3 points!!!\n"\
                                            "The resistance has won the game"
            if self.points_spies >= 3:
                self.game_state = -2
                self.message_for_group[0] = "The spies have scored 3 points!!!\n"\
                                            "The spies have won the game"

        #Method parses who the entities in a telegram message to see who is nominate
        #Changes group message and markup depending on if the nomination is valid 
        def nominate_logic(self, entities, text):
            self.ids_of_players_going_on_mission = []
            mentioned = []
            for i in range(len(entities)):
                if entities[i].type == "mention":
                    starting_index = entities[i].offset +1
                    ending_index = entities[i].offset + entities[i].length
                    username_without_at = text[starting_index:ending_index]
                    mentioned.append(username_without_at)

            if len(mentioned) != self.number_of_nominees:
                self.message_for_group[0] = ("You nominated the wrong number of players\n"\
                                             "You need to nominate "+ str(self.number_of_nominees) 
                                            +" players all in the same message")
                self.message_for_group[1] = None
                return

            for i in range(len(mentioned)):
                username = mentioned[i]
                if username not in self.players_username_to_id:
                    self.message_for_group[0] = "You nominated someone not playing"
                    self.message_for_group[1] = None
                    return
                if self.players_username_to_id[username] in self.ids_of_players_going_on_mission:
                    self.message_for_group[0] = "You nominated someone more than once"
                    self.message_for_group[1] = None
                    return
                else:
                    self.ids_of_players_going_on_mission.append(self.players_username_to_id[username])

            self.ids_of_players_voted_on_nominees = []
            self.nominees_yea_votes = 0
            self.nominees_nay_votes = 0
            
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(callback_data="yea", text="Yea"), 
                       types.InlineKeyboardButton(callback_data="nay", text="Nay"))
            
            self.message_for_group[0] = "Now everyone vote on the proposed mission party\n"\
                                        "If half or more of the vote are nay the next player"\
                                        " will get to nominate players o go on a mission"
            self.message_for_group[1] = markup
            self.game_state = 3
            return

        #Takes a players ID and vote on a mission party nomination (does not check for repeat votes)
        #Returns message of confirmation, changes game state if enough votes have been cast 
        def vote_logic(self, player_id, vote):
            if vote == "yea":
                self.nominees_yea_votes += 1
                if self.nominees_yea_votes > self.number_of_players/2:
                    self.game_state = 4
            if vote == "nay":
                self.nominees_nay_votes += 1
                if self.nominees_nay_votes >= self.number_of_players/2:
                    self.game_state = 2

            self.ids_of_players_voted_on_nominees.append(player_id)
            return "@"+ self.players_id_to_username[player_id] +" has voted "+ vote
            
        #Takes the Games group chat ID: key and generates the messages for each player on the mission
        def setup_mission(self, key):
            self.mission_pass_votes = 0
            self.mission_fail_votes = 0
            self.ids_of_players_voted_from_mission = []

            self.message_for_group[0] = ("Enough yea votes have been cast,"
                                        +self.list_usernames(None, self.ids_of_players_going_on_mission)
                                        +" are now going on a mission")
            self.message_for_group[1] = None
            
            #The key in these callbacks data are so the callback can be associated to the group chat
            markup_resistance = types.InlineKeyboardMarkup()
            markup_resistance.row(types.InlineKeyboardButton(callback_data="pass"+str(key), 
                                                             text="Pass"))
            markup_spies = types.InlineKeyboardMarkup()
            markup_spies.row(types.InlineKeyboardButton(callback_data="pass"+str(key), text="Pass"), 
                            types.InlineKeyboardButton(callback_data="fail"+str(key), text="Fail"))
           
            self.message_for_players = {}
            for player_id in self.ids_of_players_going_on_mission:
                if player_id in self.ids_of_resistances:
                    self.message_for_players[player_id] = (
                        "You are on a mission with"
                        +self.list_usernames([player_id], self.ids_of_players_going_on_mission), 
                        markup_resistance)
                if player_id in self.ids_of_spies:
                    self.message_for_players[player_id] = (
                        "You are on a mission with"
                        +self.list_usernames([player_id], self.ids_of_players_going_on_mission), 
                        markup_spies)
        
        #Takes players id and there ID and add there vote on a mission
        #If all vote from a mission are cast changes game_state and group message
        def mission_logic(self, player_id, vote):
            if vote == "pass":
                self.mission_pass_votes += 1   
            if vote == "fail" and player_id in self.ids_of_spies:
                self.mission_fail_votes += 1
            self.ids_of_players_voted_from_mission.append(player_id)

            if len(self.ids_of_players_going_on_mission) == len(self.ids_of_players_voted_from_mission):
                if (self.mission_fail_votes >= 1 and not self.two_fail_mission 
                or self.mission_fail_votes >= 2 and self.two_fail_mission):
                    self.points_spies += 1
                    self.message_for_group[0] = ("Mission fails !!!!!\n")                         
                else:
                    self.points_resistance += 1
                    self.message_for_group[0] =  ("Mission successes!!!! \n")

                self.game_round += 1
                self.message_for_group[0] += ("The score is now:\n "
                                              +str(self.points_resistance)+" for the Resistance \n"
                                              +str(self.points_spies)+" for the Spies")
                self.game_state = 2


    #An object of this class holds all the logic to play Mafia  
    class Mafia(Game):
        
        #Constructor for class 
        def __init__(self, game_code = 2, min_players = 7, max_players = 24):
            super(Mafia, self).__init__(game_code, min_players, max_players)

            """
            game_state is set to 0 in the parent class constructor
            
            game_state = 0 : game has not start (players can still join)
            game_state = 1 : the game has started (players cant hit join)
            game_state = 2 : night time waiting for all night actors to vote
            game_state = 3 : day time looking for who to lynch

            game_state - -2 : game is over about to be deleted 
            game_state = -1 : game is paused (waiting for the game to be ended or continued)
            """

            #First message to group this variable will be used to hold that will be sent to the group
            self.message_for_group[0] = "You have selected the game mafia\n"\
                                        "To play mafia we need 7 to 21 people"

            self.ids_of_innocents = []
            self.ids_of_mafiosi = []
            self.id_of_detective = None
            self.id_of_doctor = None
            self.ids_of_alive_players = []
            
            self.number_of_alive_mafiosi = 0
            self.number_of_alive_innocents = 0

            self.role_completed_mafia = False
            self.role_completed_detective = False
            self.role_completed_doctor = False

            self.id_of_saved_player = None

            self.ids_of_mafia_targets = {}
            self.ids_of_lych_targets = {}

        #Method is called once after all players have joined 
        def setup_game(self):
            self.number_of_alive_mafiosi = int(round(self.number_of_players/3))
            self.number_of_alive_innocents = self.number_of_players - self.number_of_alive_mafiosi

            self.ids_of_alive_players = self.ids_of_players
            #shuffle(self.ids_of_players)
            
            for i in range(self.number_of_alive_mafiosi):
                self.ids_of_mafiosi.append(self.ids_of_players[i])
            
            self.id_of_detective = self.ids_of_players[self.number_of_alive_mafiosi]
            self.id_of_doctor = self.ids_of_players[self.number_of_alive_mafiosi+1]
            
            for player_id in self.ids_of_players:
                if player_id not in self.ids_of_mafiosi:
                    self.ids_of_innocents.append(player_id)
                    
            self.message_for_group[0] = ("The game of Mafia has started! \nThere are "
                                        +str(self.number_of_alive_mafiosi)+ " mafiosi in the game.")
            self.message_for_group[1] = None

            for player_id in self.ids_of_innocents:
                self.message_for_players[player_id] = ("You are innocent towns person\n"\
                                                       "You win when all the mafia have been lynched", 
                                                       None)
            for player_id in self.ids_of_mafiosi:
                self.message_for_players[player_id] = ("You are a member of the Mafia\nYou win when "\
                                                       "the mafia kill off all the innocents.\n"\
                                                       "The other mafiosi are:"
                                                       +self.list_usernames([player_id], 
                                                                            self.ids_of_mafiosi), 
                                                       None)
            
            self.message_for_players[self.id_of_detective] = ("You are the Detective, you work with "\
                                                              "the towns people \nYou win when all "\
                                                              "the mafia have been lynched\nYou can "\
                                                              "learn the role of one play every night",
                                                               None)
            self.message_for_players[self.id_of_doctor] = ("You are the Doctor, you work with the "
                                                           "towns people \nYou win when all the mafia "\
                                                           "have been lynched\nYou can choose a "\
                                                           "different player each night to keep "\
                                                           "alive even if the mafia attacks them", 
                                                           None)
            #shuffle(self.ids_of_players)
            self.game_state = 2

        #Method is called after setup_game and at the start of each round 
        def setup_round(self, key):
            if self.game_state == 2:
                self.setup_night(key)
            if self.game_state == 3:
                self.setup_day()

        #Sets up for a night round, edits group and to player messages
        def setup_night(self, key):
            self.message_for_group[0] = "The night has started, the mafia are plotting to kill someone"
            self.message_for_group[1] = None
            
            self.message_for_players = {}

            markup_mafia = types.InlineKeyboardMarkup()
            for i in range(len(self.ids_of_innocents)):
                player_id = self.ids_of_innocents[i]
                if player_id in self.ids_of_alive_players:
                    player_id_index = str(i)
                    if len(player_id_index) == 1:  
                        player_id_index = "0"+player_id_index
                    markup_mafia.row(types.InlineKeyboardButton(
                        callback_data="kill"+player_id_index+str(key), 
                        text="@"+self.players_id_to_username[player_id]))

            markup_doctor = types.InlineKeyboardMarkup()
            markup_detective = types.InlineKeyboardMarkup()
            for i in range(len(self.ids_of_players)):
                player_id = self.ids_of_players[i]
                if player_id in self.ids_of_alive_players:
                    player_id_index = str(i)
                    if len(player_id_index) == 1:  
                        player_id_index = "0"+player_id_index
                    markup_doctor.row(types.InlineKeyboardButton(
                        callback_data="heal"+ player_id_index +str(key), 
                        text="@"+self.players_id_to_username[player_id]))
                    markup_detective.row(types.InlineKeyboardButton(
                        callback_data="look"+ player_id_index +str(key), 
                        text="@"+self.players_id_to_username[player_id]))

            for player_id in self.ids_of_mafiosi:
                if player_id in self.ids_of_alive_players:
                    self.message_for_players[player_id] = ("Who do you want to kill? Once all the "\
                                                           "mafia wants to kill the same person that "\
                                                           "person will be killed", 
                                                           markup_mafia)
            if self.id_of_doctor in self.ids_of_alive_players:
                self.message_for_players[self.id_of_doctor] = ("Who do you want to heal tonight?", 
                                                          markup_doctor)
            if self.id_of_detective in self.ids_of_alive_players:
                self.message_for_players[self.id_of_detective] = ("Who do you want to check the role of?", 
                                                             markup_detective)
            self.ids_of_mafia_targets = {}

        #Takes Target ID and Mafia member ID 
        #Changes role_complete to true when all mafia are voting for same person
        def kill_vote_logic(self, mafia_id, id_of_player_voted_to_be_killed, key):
            self.ids_of_mafia_targets[mafia_id] = id_of_player_voted_to_be_killed

            markup_mafia = types.InlineKeyboardMarkup()
            for i in range(len(self.ids_of_innocents)):
                player_id = self.ids_of_innocents[i]
                if player_id in self.ids_of_alive_players:
                    player_id_index = str(i)
                    if len(player_id_index) == 1:  
                        player_id_index = "0" + player_id_index
                
                    vote_count = 0
                    for targeter_id in self.ids_of_mafia_targets: 
                        if self.ids_of_mafia_targets[targeter_id]==player_id:
                            vote_count = vote_count + 1

                    markup_mafia.row(types.InlineKeyboardButton(
                        callback_data="kill"+ player_id_index +str(key), 
                        text="@"+self.players_id_to_username[player_id]+str(vote_count)))

                    if vote_count == self.number_of_alive_mafiosi:
                        self.role_completed_mafia = True 

            for player_id in self.ids_of_mafiosi:
                if player_id in self.ids_of_alive_players:
                    self.message_for_players[player_id] = ("Who do you want to kill? Once all the "\
                                                           "mafia wants to kill the same person that "\
                                                           "person will be killed", 
                                                           markup_mafia)

        #Takes ID of doctors target and returns message to be sent to doctor 
        def doctor_logic(self, id_of_player_to_save):
            self.role_completed_doctor = True
            if (self.id_of_saved_player != id_of_player_to_save 
            and id_of_player_to_save in self.ids_of_alive_players):
                self.id_of_saved_player = id_of_player_to_save
                return "@"+ self.players_id_to_username[id_of_player_to_save] +" will be saved"
            else:
                self.role_completed_doctor = False
                return "They can not be saved"

        #Takes player ID returns message saying what role that player has 
        def detective_logic(self, id_of_player_to_search):
            self.role_completed_detective = True
            if id_of_player_to_search in self.ids_of_innocents:
                if id_of_player_to_search == self.id_of_doctor:
                    return "@"+self.players_id_to_username[id_of_player_to_search]+" is the doctor."
                else:
                    return "@"+self.players_id_to_username[id_of_player_to_search] \
                           +" is an innocent towns person."
            if id_of_player_to_search in self.ids_of_mafiosi:
                return "@"+self.players_id_to_username[id_of_player_to_search]+" is part of the mafia."

        #Returns true and changes game state if all night role actions have been preformed 
        def night_over(self):
            if (self.role_completed_mafia 
            and self.role_completed_detective
            and self.role_completed_doctor):
                self.game_state = 3
                return True
            else:
                return False

        #Method called to set up game for a day round
        def setup_day(self):
            #all the keys in mafia targets should point to the same value
            id_of_victim = self.ids_of_mafia_targets.values()[0]

            victim_kill = id_of_victim != self.id_of_saved_player

            if victim_kill:
                self.message_for_group[0] = ("During the night @" 
                                             +self.players_id_to_username[id_of_victim] 
                                             +" was killed by the mafia\n\nIt is now the day, "\
                                             "who should be lynched?\nIf half or more of the "\
                                             "players are voting for someone they will be lynched")       
                self.ids_of_alive_players.remove(id_of_victim)
                self.number_of_alive_innocents = self.number_of_alive_innocents - 1
            else:
                self.message_for_group[0] = ("During the night @" 
                                            +self.players_id_to_username[id_of_victim] 
                                            +" was attacked by the mafia, luckily the doctor also "\
                                            "visited that night and saved a life\n\nIt is now the "\
                                            "day, who should be lynched?\nIf half or more of the "\
                                            "players are voting for someone they will be lynched")

            markup_day = types.InlineKeyboardMarkup()
            for player_id in self.ids_of_players:
                if player_id in self.ids_of_alive_players:
                    markup_day.row(types.InlineKeyboardButton(
                        callback_data="lynch"+ str(player_id), 
                        text="@"+self.players_id_to_username[player_id]))

            self.message_for_group[1] = markup_day
            self.ids_of_lych_targets = {}

        #Called when someone votes for someone to be lynched, changes group message and markup
        #returns a players ID if vote is the last voted needed to lynch someone otherwise returns False
        def lynch_logic(self, voter_id, id_of_player_to_be_lyched):
            self.ids_of_lych_targets[voter_id] = id_of_player_to_be_lyched

            markup_lynch = types.InlineKeyboardMarkup()
            for player_id in self.ids_of_alive_players:
                vote_count = 0
                for targeter_id in self.ids_of_lych_targets: 
                    if self.ids_of_lych_targets[targeter_id]==player_id:
                        vote_count = vote_count + 1
                
                markup_lynch.row(types.InlineKeyboardButton(
                    callback_data="lynch"+str(player_id), 
                    text="@"+self.players_id_to_username[player_id]+" "+str(vote_count)))
                
                if vote_count >= ((self.number_of_alive_mafiosi + self.number_of_alive_innocents)/2.0):
                    self.ids_of_alive_players.remove(player_id)
                    if player_id in self.ids_of_mafiosi:
                        self.number_of_alive_mafiosi = self.number_of_alive_mafiosi - 1
                    if player_id in self.ids_of_innocents:
                        self.number_of_alive_innocents = self.number_of_alive_innocents - 1
                    self.message_for_group[1] = markup_lynch
                    self.game_state = 2
                    return id_of_player_to_be_lyched

            self.message_for_group[1] = markup_lynch
            return False

        #Method will change group message and game_state if a victory state is reached
        def check_for_winner(self):
            if self.number_of_alive_innocents == 0:
                self.message_for_group[0] = "The last innocent has been killed the Mafia Win!!!"
                self.game_state = -2

            if self.number_of_alive_mafiosi == 0:
                self.message_for_group[0] = "The last mafiosi has been killed the Towns people Win!!!"
                self.game_state = -2

