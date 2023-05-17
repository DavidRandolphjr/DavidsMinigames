
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import Room, Checkers, Lobby, Monopoly
from .models import User
import ast
import random
import time

class Game:
    def __init__(self, playerone, playertwo, kings, who,roomid=None,):
        self.playerone = playerone
        self.playertwo = playertwo
        self.kings = kings
        self.openspaces = []
        self.roomid = roomid
        self.who = who
        for i in range(0,8):
            for j in range(0,4):
                k=j*2
                l=j*2 +1
                if i % 2 == 0:
                    if not [i,k] in playerone and not [i,k] in playertwo:
                        self.openspaces.append([i,k])
                if i % 2 != 0:
                    if not [i,l] in playerone and not [i,l] in playertwo:
                        self.openspaces.append([i,l])

        self.moves_available = []
        #self.moves_safe could be unimportant. Perhaps it can save time though with certain applications
        self.moves_safe = []
        self.no_consequence_jump = []
        self.pos_at_risk = []
        #this is to see if a checker can slide inbetween checkers of playerone and playertwo
        self.holes_exist = []
        self.jumps_available=[]
    def available_moves(self):
        def one_moves(pieces):
            for i in pieces:
                if [i[0]+1,i[1]-1] in self.openspaces:

                    self.moves_available.append([i,[i[0]+1,i[1]-1]])
                if [i[0]+1,i[1]+1] in self.openspaces:
                    
                    self.moves_available.append([i,[i[0]+1,i[1]+1]])
                if self.who == self.playerone and i in self.kings:
                    two_moves([i])
        def two_moves(pieces):
            for i in pieces:
                if [i[0]-1,i[1]-1] in self.openspaces:

                    self.moves_available.append([i,[i[0]-1,i[1]-1]])
                if [i[0]-1,i[1]+1] in self.openspaces:

                    self.moves_available.append([i,[i[0]-1,i[1]+1]])
                if self.who == self.playertwo and i in self.kings:
                    one_moves([i])

        # have to change these
        if self.who == self.playerone:
            one_moves(self.playerone)

        if self.who == self.playertwo:
            two_moves(self.playertwo)




        return (self.moves_available)
    # this is going to be for the AI. I have not taken kings into account yet when determining safe moves
    def in_danger(self):
        exposures = []
        def at_risk(pieces, player):
            exposures = [] # counts the spot where an opposing checker could land with a jump
            # we could take this information and either have the player move another checker to cover the exposure
            # or we could try to move the checker safely out of the way if possible
            if player == "playerone":
                
                if [pieces[0]+1, pieces[1]-1] in self.playertwo and [pieces[0]-1, pieces[1]+1] in self.openspaces:
                    exposures.append([pieces[0]-1, pieces[1]+1])
                if [pieces[0] + 1, pieces[1] + 1] in self.playertwo and [pieces[0] - 1, pieces[1] - 1] in self.openspaces:
                    
                    exposures.append([pieces[0] - 1, pieces[1] - 1])
                if [pieces[0]-1, pieces[1] - 1] in self.playertwo and [pieces[0]-1, pieces[1] - 1] in self.kings and [pieces[0] + 1, pieces[1] + 1] in self.openspaces:
                    exposures.append([pieces[0] + 1, pieces[1] + 1])
                if [pieces[0]-1, pieces[1] + 1] in self.playertwo and [pieces[0]-1, pieces[1] + 1] in self.kings and [pieces[0] + 1, pieces[1] - 1] in self.openspaces:
                    exposures.append([pieces[0] + 1, pieces[1] - 1])
            if player == "playertwo":
                if [pieces[0]-1, pieces[1]-1] in self.playerone and [pieces[0]+1, pieces[1]+1] in self.openspaces:
                    exposures.append([pieces[0]+1, pieces[1]+1])
                if [pieces[0] - 1, pieces[1] + 1] in self.playerone and [pieces[0] + 1, pieces[1] - 1] in self.openspaces:
                    exposures.append([pieces[0] + 1, pieces[1] - 1])
                if [pieces[0]+1, pieces[1] - 1] in self.playerone and [pieces[0]+1, pieces[1] - 1] in self.kings and [pieces[0] - 1, pieces[1] + 1] in self.openspaces:
                    exposures.append([pieces[0] - 1, pieces[1] + 1])
                if [pieces[0]+1, pieces[1] + 1] in self.playerone and [pieces[0]+1, pieces[1] + 1] in self.kings and [pieces[0] - 1, pieces[1] - 1] in self.openspaces:
                    exposures.append([pieces[0] - 1, pieces[1] - 1])
            return exposures

        if self.who == self.playertwo:
            for i in self.playertwo:

                if len(at_risk(i, "playertwo")) >0:
                    self.pos_at_risk.append([i, at_risk(i, "playertwo")])
            return ("these are the safe jumps", self.pos_at_risk)

        if self.who == self.playerone:
            for i in self.playerone:
                if len(at_risk(i, "playerone")) > 0:
                    self.pos_at_risk.append([i, at_risk(i, "playerone")])
            return ("these are the safe jumps", self.pos_at_risk)
        
    def safe_moves(self):
        self.moves_safe = self.moves_available.copy()
        if self.who == self.playerone:
            for i in self.moves_available:
                temp_playerone = self.playerone.copy()
                temp_playerone.remove(i[0])
                temp_playerone.append(i[1])
                is_move_safe = Game(temp_playerone, self.playertwo, self.kings,temp_playerone, None)
                is_move_safe.in_danger()
                if len(self.pos_at_risk) <= len(is_move_safe.pos_at_risk):
                    self.moves_safe.remove(i)
                
        if self.who == self.playertwo:
            
            for i in self.moves_available:
                temp_playertwo = self.playertwo.copy()
                temp_playertwo.remove(i[0])
                temp_playertwo.append(i[1])
                is_move_safe = Game(self.playerone, temp_playertwo, self.kings,temp_playertwo, None)
                is_move_safe.in_danger()
                
                if self.pos_at_risk != is_move_safe.pos_at_risk:
                    if len(self.pos_at_risk) <= len(is_move_safe.pos_at_risk):

                        
                        self.moves_safe.remove(i) 
                        
    def jumps(self):
        def one_jumps(pieces, one_ahead, two_ahead):
            if self.who == self.playerone:
                oposer = self.playertwo
            else:
                oposer = self.playerone
            for i in pieces:
                

                self.jumps = []
                the_range = 1
                if i in self.kings:
                    the_range = 2
                for k in range(0,the_range):
                    if [i[0]+one_ahead, i[1]+1] in oposer and [i[0]+two_ahead, i[1]+2] in self.openspaces:
                        self.jumps.append([i[0]+two_ahead, i[1]+2])
                        # the problem here is that we add to jumps_available two jumps if a available. the problem here is that only one jump can be made at a time.
                        # I need to figure out a way to separate the list when two different directional jumps are available.
                        # i thing we could do math or something here. like if abs(self.jumps[-1][0] - j[1]+2) != 2: delete self.jumps[-1] and add [j[0] + two_ahead, j[1] - 2].
                        # however, this is a for loop and messes up the loop for the next interation.
                        for j in self.jumps:

                            if [j[0]+one_ahead, j[1]+1] in oposer and [j[0]+two_ahead, j[1]+2] in self.openspaces:
                                if not [j[0]+two_ahead, j[1]+2] in self.jumps:
                                    self.jumps.append([j[0]+two_ahead, j[1]+2])
                            if [j[0] + one_ahead, j[1] - 1] in oposer and [j[0] + two_ahead, j[1] - 2] in self.openspaces:
                                if not [j[0]+two_ahead, j[1]-2] in self.jumps:
                                    self.jumps.append([j[0] + two_ahead, j[1] - 2])
                            if the_range ==2:
                                if [j[0]+one_ahead*-1, j[1]+1] in oposer and [j[0]+two_ahead*-1, j[1]+2] in self.openspaces:
                                    if not [j[0]+two_ahead*-1, j[1]+2] in self.jumps:
                                        self.jumps.append([j[0]+two_ahead*-1, j[1]+2])
                                if [j[0] + one_ahead*-1, j[1] - 1] in oposer and [j[0] + two_ahead*-1, j[1] - 2] in self.openspaces:
                                    if not [j[0] + two_ahead*-1, j[1] - 2] in self.jumps:
                                        self.jumps.append([j[0] + two_ahead*-1, j[1] - 2])
                    if the_range >1:
                        one_ahead *=-1
                        two_ahead *=-1
                
                if len(self.jumps)>0:
                    self.jumps_available.append([i, self.jumps])
                self.jumps = []
                for k in range(0,the_range):
                    if [i[0]+one_ahead, i[1]-1] in oposer and [i[0]+two_ahead, i[1]-2] in self.openspaces:
                        self.jumps.append([i[0]+two_ahead, i[1]-2])
                        for j in self.jumps:

                            if [j[0]+one_ahead, j[1]+1] in oposer and [j[0]+two_ahead, j[1]+2] in self.openspaces:
                                if not [j[0]+two_ahead, j[1]+2] in self.jumps:
                                    self.jumps.append([j[0]+two_ahead, j[1]+2])
                            if [j[0] + one_ahead, j[1] - 1] in oposer and [j[0] + two_ahead, j[1] - 2] in self.openspaces:
                                if not [j[0]+two_ahead, j[1]-2] in self.jumps:
                                    self.jumps.append([j[0] + two_ahead, j[1] - 2])
                            if the_range ==2:
                                if [j[0]+one_ahead*-1, j[1]+1] in oposer and [j[0]+two_ahead*-1, j[1]+2] in self.openspaces:
                                    if not [j[0]+two_ahead*-1, j[1]+2] in self.jumps:
                                        self.jumps.append([j[0]+two_ahead*-1, j[1]+2])
                                if [j[0] + one_ahead*-1, j[1] - 1] in oposer and [j[0] + two_ahead*-1, j[1] - 2] in self.openspaces:
                                    if not [j[0] + two_ahead*-1, j[1] - 2] in self.jumps:
                                        self.jumps.append([j[0] + two_ahead*-1, j[1] - 2])
                    if the_range >1:
                        one_ahead *=-1
                        two_ahead *=-1
                
                if len(self.jumps)>0:
                    self.jumps_available.append([i, self.jumps])
                if i in self.kings and [i] != pieces:
                    one_jumps([i], one_ahead*-1,two_ahead*-1)

        if self.who == self.playertwo:
            one_jumps(self.playertwo, -1,-2)

        if self.who == self.playerone:
            one_jumps(self.playerone, 1,2)

        return (self.jumps_available)
    

    # safe_jumps does not account for kings. To determine if a jump is safe against a king, we will just have to check if a king has a jump in the opposite direction
    def safe_jumps(self):
        first_player = self.playerone.copy()
        self.no_consequence_jump = self.jumps_available.copy()
        kinged = self.kings.copy()
        print("THIS IS FIRST_PLAYER THOUGH", first_player)
        if self.who == self.playerone:
            for i in self.jumps_available:
                first_player[first_player.index(i[0])] = i[1][-1]
                if i[0] in kinged:
                    kinged[kinged.index(i[0])] = i[1][-1]
                checker_removal = self.playertwo.copy()
                
                if i[1][-1][0] == 7:
                    if not i[1][-1] in kinged:
                        kinged.append(i[1][-1])
                # this little function right here is to specify the jumps that are being made. The aim is to eliminate a jump option if there are two jumps present on the same row.
                listy = i[1][::-1]
                newlist = [listy[0]]
                last_value = listy[0]
                for j in range(0, len(listy)-1):

                    if abs(last_value[1] -listy[j+1][1]) ==2 and abs(last_value[0] -listy[j+1][0]) ==2:
                        
                        newlist.append(listy[j+1])
                        last_value = listy[j+1]
                i[1]=newlist[::-1]
                
                temp_value = i[0]
                
                
                for j in i[1]:
                    #here lies the problem. Jumped doesnt put the right thing for double jumps
                    
                    # the issue lies here for the second jump
                    jumped = [int(abs(temp_value[0]+j[0])/2), int(abs(temp_value[1]+j[1])/2)]
                    temp_value = j
                    
                    try:
                        
                        checker_delete =ast.literal_eval(checker_removal)
                        checker_delete.remove(jumped)
                        checker_delete = checker_delete
                        
                        checker_removal= checker_delete
                        
                        
                    except:
                        pass
                
                
                temp_player_two = checker_removal
                is_jump_safe = Game(first_player, temp_player_two, kinged,first_player, None)
                is_jump_safe.in_danger()
                if self.pos_at_risk <= is_jump_safe.pos_at_risk:
                    self.no_consequence_jump.remove(i)
        else:
            for i in self.jumps_available:
                first_player = self.playertwo.copy()
                first_player[first_player.index(i[0])] = i[1][-1]
                if i[0] in kinged:
                    kinged[kinged.index(i[0])] = i[1][-1]
                    
                checker_removal = self.playerone.copy()
                
                if i[1][-1][0] == 0:
                    if not i[1][-1] in kinged:
                        kinged.append(i[1][-1])
                listy = i[1][::-1]
                newlist = [listy[0]]
                last_value = listy[0]
                for j in range(0, len(listy)-1):

                    if abs(last_value[1] -listy[j+1][1]) ==2 and abs(last_value[0] -listy[j+1][0]) ==2:
                        
                        newlist.append(listy[j+1])
                        last_value = listy[j+1]
                i[1]=newlist[::-1]
                
                temp_value = i[0]
                
                
                for j in i[1]:
                    #here lies the problem. Jumped doesnt put the right thing for double jumps
                    
                    # the issue lies here for the second jump
                    jumped = [int(abs(temp_value[0]+j[0])/2), int(abs(temp_value[1]+j[1])/2)]
                    temp_value = j
                    
                    try:
                        
                        checker_delete =checker_removal
                        checker_delete.remove(jumped)
                        
                        
                        checker_removal= checker_delete
                        
                        
                    except:
                        pass
                
                if self.who == self.playertwo:
                    
                    temp_player_one = checker_removal
                else:
                    
                    temp_player_two = checker_removal
                temp_player_one = checker_removal
                
                is_jump_safe = Game(temp_player_one, first_player, kinged,first_player, None)
                is_jump_safe.in_danger()
                
                if self.pos_at_risk != is_jump_safe.pos_at_risk:
                    if len(self.pos_at_risk) <= len(is_jump_safe.pos_at_risk):
                        
                        self.no_consequence_jump.remove(i)
                else:
                    pass
        
                        
        
                
            return ("these are the safe jumps", self.no_consequence_jump)
    def moved(self, where, roomid):
        
        
        where[1]=where[1][:where[1].index(where[1][-1])+1]
        

        self.roomid = roomid
        first_player = self.playerone.copy()
        

        
        the_game = Checkers.objects.get(roomid = roomid)
        kinged = ast.literal_eval(the_game.kings)
        
        # Figure out who's turn it is
        player_turn = the_game.team_owner.split()
        player_turns = len(player_turn)
        if self.who == self.playerone:
            
            first_player[first_player.index(where[0])] = where[1][-1]
            if where[0] in kinged:
                kinged[kinged.index(where[0])] = where[1][-1]
                the_game.kings = str(kinged)
            
            next_turn = player_turn[player_turn.index(the_game.turn) +1]
            checker_removal = the_game.player_two
            the_game.player_one = str(first_player)
            if where[1][-1][0] == 7:
                if not where[1][-1] in kinged:
                    kinged.append(where[1][-1])
                    the_game.kings = str(kinged)
        else:
            next_turn = player_turn[0]
            first_player = self.playertwo.copy()
            first_player[first_player.index(where[0])] = where[1][-1]
            if where[0] in kinged:
                kinged[kinged.index(where[0])] = where[1][-1]
                the_game.kings = str(kinged)
            checker_removal = the_game.player_one
            the_game.player_two = str(first_player)
            if where[1][-1][0] == 0:
                if not where[1][-1] in kinged:
                    kinged.append(where[1][-1])
                    the_game.kings = str(kinged)
        the_game.turn = next_turn
        # this little function right here is to specify the jumps that are being made. The aim is to eliminate a jump option if there are two jumps present on the same row.
        listy = where[1][::-1]
        newlist = [listy[0]]
        last_value = listy[0]
        for i in range(0, len(listy)-1):

            if abs(last_value[1] -listy[i+1][1]) ==2 and abs(last_value[0] -listy[i+1][0]) ==2:
                
                newlist.append(listy[i+1])
                last_value = listy[i+1]
        where[1]=newlist[::-1]
        
        temp_value = where[0]
        
        
        for i in where[1]:
            #here lies the problem. Jumped doesnt put the right thing for double jumps
            
            # the issue lies here for the second jump
            jumped = [int(abs(temp_value[0]+i[0])/2), int(abs(temp_value[1]+i[1])/2)]
            temp_value = i
            
            try:
                
                checker_delete =ast.literal_eval(checker_removal)
                checker_delete.remove(jumped)
                checker_delete = str(checker_delete)
                
                checker_removal= checker_delete
                if jumped in self.kings:
                    print("jumped",jumped, "was in self.kings", self.kings)
                    self.kings.remove(jumped)
                    the_game.kings = self.kings
                    print("This is self.kings", self.kings)
                
            except:
                pass
        
        if self.who == self.playertwo:
            
            the_game.player_one = checker_removal
            
        else:
            
            the_game.player_two = checker_removal
            
        
        the_game.save()
        print("__________________________________________________")
class Game_monopoly:
    def __init__(self, current_instance,roomid=None,):
        self.current_instance = current_instance
        self.playerone = ast.literal_eval(current_instance.player_one)
        self.playertwo = ast.literal_eval(current_instance.player_two)
        self.playerthree = ast.literal_eval(current_instance.player_three)
        self.playerfour = ast.literal_eval(current_instance.player_four)
        self.positions = ast.literal_eval(current_instance.positions)
        self.available_prop= ast.literal_eval(current_instance.available_prop)
        self.money = ast.literal_eval(current_instance.money)
        self.who = current_instance.turn
        self.teamowners = current_instance.team_owner.split()
        # self.turn returns the index of who's turn it is
        self.turn = current_instance.turn_index
        self.themove= ""
        self.property_cost = {
            "1": ["MEDITERRANEAN AVENUE",60],
            "3": ["BALTIC AVENUE",60],
            "5": ["READING RAILROAD",200],
            "6": ["ORIENTAL AVENUE",100],
            "8": ["VERMONT AVENUE",100],
            "9": ["CONNECTICUT AVENUE",120],
            "11": ["ST.CHARLES PLACE",140],
            "12": ["ELECTRIC COMPANY",150],
            "13": ["STATES AVENUE",140],
            "14": ["VIRGINIA AVENUE", 160],
            "15": [200],
            "16": [180],
            "18": [180],
            "19": [200],
            "21": [220],
            "23": [220],
            "24": [240],
            "25": [200],
            "26": [260],
            "27": [260],
            "28": [150],
            "29": [280],
            "31": [300],
            "32": [300],
            "34": [320], 
            "35": [200],
            "37": [350],
            "39": [400],


        }
        
    def roll_dice(self):
        print("most importantly, made it here")
        roll = random.randrange(2, 12)
        self.positions[self.turn] += roll 

        self.current_instance.positions = str(self.positions)
        
        self.current_instance.rolled_dice = True
        self.current_instance.themove = "rolled a %s" % roll
        self.current_instance.save()
        
        
        return(self.themove)
    
    def end_turn(self):
        # might have to move this piece to an "end move" function
        if self.turn <3:
            self.current_instance.turn = self.teamowners[self.turn +1]
            self.current_instance.turn_index +=1
        else:
            self.current_instance.turn = self.teamowners[0]
            self.current_instance.turn_index =0
        self.current_instance.themove = "ended turn"
        self.current_instance.save()
        return()
        
    def purch_available(self):
        # self.positions[self.current_instance.turn_index] is the spot the current player is on
        print("whats this", self.positions[self.turn])
        try:
            if self.positions[self.current_instance.turn_index] in self.available_prop and self.money[self.turn]> self.property_cost[str(self.positions[self.turn])]:
                return("Purchase available")
            else:
                return("Not available for purchase / insufficient funds")
        except:
            return("Not available for purchase / insufficient funds")
    
    def purchased(self):
        print("got into purchased")
        player_list = [self.playerone, self.playertwo, self.playerthree, self.playerfour]
        # we save the added property to self.playerwhatever first because it is an actual list
        
        player_list[self.turn].append(self.positions[self.current_instance.turn_index])
        # then we convert it to a string and save it to the actual model table
        print("this is what is owned", player_list[self.turn])
        if self.turn ==0:
            self.current_instance.player_one = str(player_list[self.turn])
        elif self.turn ==1:
            self.current_instance.player_two = str(player_list[self.turn])
        elif self.turn ==2:
            self.current_instance.player_three = str(player_list[self.turn])
        else:
            self.current_instance.player_four = str(player_list[self.turn])
        
        # remove property from available property list
        
        self.available_prop.remove(self.positions[self.turn])
        # covert property list to string and save to actual model table
        
        self.current_instance.available_prop = str(self.available_prop)
        # self.themove is equal to a placeholder. We ultimately want it to way what was purchased, not a number

        self.money[self.turn] -=self.property_cost[str(self.positions[self.turn])]

        self.current_instance.money = str(self.money)
        
        self.current_instance.themove = "purchased %s" % self.positions[self.turn]
        
        self.current_instance.save()
        return()

def checkers_game(current_instance, moved=None, aiturn=None):
    player_instance = current_instance.player_one
    
    if current_instance.turn == "AI":

        player_instance = current_instance.player_two

    game_instance = Game(ast.literal_eval(current_instance.player_one), ast.literal_eval(current_instance.player_two), ast.literal_eval(current_instance.kings),ast.literal_eval(player_instance), current_instance.roomid)
    game_instance.available_moves()
    game_instance.jumps()
    print("this is who's turn it is %s" % current_instance.turn )
    if aiturn:
        
        game_instance.in_danger()
        game_instance.safe_moves()
        game_instance.safe_jumps()
        print("we made it all the way here", player_instance)
        print("moves available",game_instance.moves_available)
        print("safe moves", game_instance.moves_safe)
        print("spots in danger", game_instance.pos_at_risk)
        print("safe jumps", game_instance.no_consequence_jump)
        print("jumps",game_instance.jumps_available )
        taskfulfilled = False
        # there are values in maxjump so that the if condition does not give an error
        max_len = -1
        res = [1,[1]]
        if len(game_instance.jumps_available)>0:
            for ele in game_instance.jumps_available:

                if len(ele[1]) > max_len:
                    max_len = len(ele[1])
                    res = ele
        
        
        if len(res[1])>1:
            print("AI made multi-jump")
            game_instance.moved(res, current_instance.roomid)
        # priority two, get checkers out of risk
        elif len(game_instance.pos_at_risk) >0:
             
            for i in game_instance.pos_at_risk:
                # sub-priority one, perform safe jump with at risk checker if possible
                for j in game_instance.no_consequence_jump:
                    if i[0] == j[0]:
                        print("AI did a safe jump", [j[0],j[1]])
                        game_instance.moved([j[0],j[1]], current_instance.roomid)
                        taskfulfilled = True
                        break
                if taskfulfilled == True:
                    break
                # sub-priority two, perform safe move with at risk checker if possible
                for k in game_instance.moves_safe:
                    print("LEARNING HERE______", i[0], k[0])
                    if i[0] == k[0]:
                        print("AI did a safe move",[k[0],[k[1]]])
                        game_instance.moved([k[0],[k[1]]], current_instance.roomid)
                        taskfulfilled = True
                        break
                    # sub-priority three, cover at risk spot with another checker
                if taskfulfilled:
                    break
                for k in game_instance.moves_safe:
                    if k[1] in i[1]:
                        print("AI did a block move",[k[0],[k[1]]])
                        game_instance.moved([k[0],[k[1]]], current_instance.roomid)
                        taskfulfilled = True
                        break
                if taskfulfilled == False:
                    if len(game_instance.no_consequence_jump)>0:
                        
                        rand_num =len(game_instance.no_consequence_jump)-1
                        print("SAFE JUMP HAPPENED",[game_instance.no_consequence_jump[rand_num][0],game_instance.no_consequence_jump[rand_num][1]])
                        game_instance.moved([game_instance.no_consequence_jump[rand_num][0],game_instance.no_consequence_jump[rand_num][1]], current_instance.roomid)
                    elif len(game_instance.moves_safe)>0:
                        
                        rand_num =len(game_instance.moves_safe)-1
                        print("SAFE MOVE CHOSEN", [game_instance.moves_safe[rand_num][0],[game_instance.moves_safe[rand_num][1]]])
                        game_instance.moved([game_instance.moves_safe[rand_num][0],[game_instance.moves_safe[rand_num][1]]], current_instance.roomid)
                        taskfulfilled = True
                        
                    elif len(game_instance.jumps_available)>0:
                        
                        rand_num =len(game_instance.jumps_available)-1
                        print("RANDOM JUMP HERE",[game_instance.jumps_available[rand_num][0],[game_instance.jumps_available[rand_num][1]]])
                        game_instance.moved([game_instance.jumps_available[rand_num][0],[game_instance.jumps_available[rand_num][1]]], current_instance.roomid)
                        taskfulfilled = True
                        
                    # priority five, make random move
                    else:
                        
                        rand_num =len(game_instance.moves_available)-1
                        print("RANDOM MOVE SELECTED", [game_instance.moves_available[rand_num][0],[game_instance.moves_available[rand_num][1]]])
                        game_instance.moved([game_instance.moves_available[rand_num][0],[game_instance.moves_available[rand_num][1]]], current_instance.roomid)
                        taskfulfilled = True
                else:
                    break
                    
                if taskfulfilled == True:
                    break
        # make safe jump
        elif len(game_instance.no_consequence_jump)>0:
            
            rand_num =len(game_instance.no_consequence_jump)-1
            print("SAFE JUMP HAPPENED", [game_instance.no_consequence_jump[rand_num][0],game_instance.no_consequence_jump[rand_num][1]])
            game_instance.moved([game_instance.no_consequence_jump[rand_num][0],game_instance.no_consequence_jump[rand_num][1]], current_instance.roomid)
        # priority three, make random safe move
        elif len(game_instance.moves_safe)>0:
            
            rand_num =len(game_instance.moves_safe)-1
            print("SAFE MOVE HAPPENED", [game_instance.moves_safe[rand_num][0],[game_instance.moves_safe[rand_num][1]]])
            game_instance.moved([game_instance.moves_safe[rand_num][0],[game_instance.moves_safe[rand_num][1]]], current_instance.roomid)
        # priority four, make random jump
        elif len(game_instance.jumps_available)>0:
            
            rand_num =len(game_instance.jumps_available)-1
            print("REGULAR JUMP", [game_instance.jumps_available[rand_num][0],game_instance.jumps_available[rand_num][1]])
            game_instance.moved([game_instance.jumps_available[rand_num][0],game_instance.jumps_available[rand_num][1]], current_instance.roomid)
        # priority five, make random move
        else:
            
            rand_num =len(game_instance.moves_available)-1
            print("RANDOM MOVE TIME", [game_instance.moves_available[rand_num][0],[game_instance.moves_available[rand_num][1]]])
            game_instance.moved([game_instance.moves_available[rand_num][0],[game_instance.moves_available[rand_num][1]]], current_instance.roomid)
        
        # the ai is gonna have to know when its in danger and how to get out of it.
        # I am thinking im going to make a "in_danger" definition that checks for checkers in front and open spaces in the back. 
        # Checking for safety against a king will just be tedius. 
    if moved:
        
        game_instance.moved(moved, current_instance.roomid)
    return ([{
        "player_one": ast.literal_eval(current_instance.player_one), 
        "player_two": ast.literal_eval(current_instance.player_two), 
        "kings": ast.literal_eval(current_instance.kings),
        "available_space": game_instance.available_moves(), #at the moment we are only catering to player one
        "jumps": game_instance.jumps_available,
        "open_spaces": game_instance.openspaces ,
        "player_turn": current_instance.turn,

        }])

def monopoly_game(current_instance, moved=None, aiturn=None):
    # Havent come up with anything yet
    
    game_instance = Game_monopoly(current_instance)
    if moved:
        
        move_options = {
            "roll": game_instance.roll_dice,
            "endturn": game_instance.end_turn,
            "purchased": game_instance.purchased,

        }
        move_options[moved]()
        print("this is themove", game_instance.themove)
    return ([{
        "player_turn": current_instance.turn,
        "rolled_dice": current_instance.rolled_dice,
        "positions": ast.literal_eval(current_instance.positions),
        "money": ast.literal_eval(current_instance.money),
        "themove": current_instance.themove,
        "turn_index": current_instance.turn_index,
        "purch_available": str(game_instance.purch_available()),

        }])



def dice_game():
    return 6