
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import Room, Checkers, Dice, Lobby
from .models import User
import ast
import random

class Game:
    def __init__(self, playerone, playertwo, kings, roomid=None):
        self.playerone = playerone
        self.playertwo = playertwo
        self.kings = kings
        self.openspaces = []
        self.roomid = roomid
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
    def available_moves(self, who):
        def one_moves(pieces):
            for i in pieces:
                if [i[0]+1,i[1]-1] in self.openspaces:

                    self.moves_available.append([i,[i[0]+1,i[1]-1]])
                if [i[0]+1,i[1]+1] in self.openspaces:
                    
                    self.moves_available.append([i,[i[0]+1,i[1]+1]])
                if who == self.playerone and i in self.kings:
                    two_moves([i])
        def two_moves(pieces):
            for i in pieces:
                if [i[0]-1,i[1]-1] in self.openspaces:

                    self.moves_available.append([i,[i[0]-1,i[1]-1]])
                if [i[0]-1,i[1]+1] in self.openspaces:

                    self.moves_available.append([i,[i[0]-1,i[1]+1]])
                if who == self.playertwo and i in self.kings:
                    one_moves([i])

        # have to change these
        if who == self.playerone:
            one_moves(self.playerone)

        if who == self.playertwo:
            two_moves(self.playertwo)




        return (self.moves_available)
    # this is going to be for the AI. I have not taken kings into account yet when determining safe moves
    def in_danger(self, who):
        exposures = []
        def at_risk(pieces, player):
            exposures = [] # counts the spot where an opposing checker could land with a jump
            # we could take this information and either have the player move another checker to cover the exposure
            # or we could try to move the checker safely out of the way if possible
            if player == "playerone":
                print(pieces, )
                if [pieces[0]+1, pieces[1]-1] in self.playertwo and [pieces[0]-1, pieces[1]+1] in self.openspaces:
                    exposures.append([pieces[0]-1, pieces[1]+1])
                if [pieces[0] + 1, pieces[1] + 1] in self.playertwo and [pieces[0] - 1, pieces[1] - 1] in self.openspaces:
                    print("this triggered for ", pieces)
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

        if who == self.playertwo:
            for i in self.playertwo:

                if len(at_risk(i, "playertwo")) >0:
                    self.pos_at_risk.append([i, at_risk(i, "playertwo")])
            return ("these are the safe jumps", self.pos_at_risk)

        if who == self.playerone:
            for i in self.playerone:
                if len(at_risk(i, "playerone")) > 0:
                    self.pos_at_risk.append([i, at_risk(i, "playerone")])
            return ("these are the safe jumps", self.pos_at_risk)
        
    def safe_moves(self, who):
        if who == self.playerone:
            for i in self.moves_available:
                #check to see if spot ahead of moves_available is open.
                if not [i[1][0] + 1, i[1][1] - 1] in self.playertwo and not [i[1][0] + 1, i[1][1] + 1] in self.playertwo:
                    if not [i[1][0] - 1, i[1][1] - 1] in self.playertwo and not [i[1][0] - 1, i[1][1] - 1] in self.kings or [i[1][0] - 1, i[1][1] + 1] in self.playertwo and not [i[1][0] - 1, i[1][1] + 1] in self.kings:
                        self.moves_safe.append(i)
            for i in self.playerone:

                if [i[0]+2,i[1]-2] in self.playertwo and not [i[0]+2,i[1]] in self.playertwo:

                    if [i[0],i[1]-2] in self.openspaces:
                        self.holes_exist.append([i, [i[0]+1,i[1]-1]])
                if [i[0]+2,i[1]+2] in self.playertwo and not [i[0]+2,i[1]] in self.playertwo:

                    if [i[0], i[1] + 2] in self.openspaces:
                        self.holes_exist.append([i, [i[0]+1,i[1]+1]])
            self.moves_safe.extend(self.holes_exist)
            return ("safe moves",self.moves_safe)

        if who == self.playertwo:
            for i in self.moves_available:
                #check to see if spot ahead of moves_available is open.
                if not [i[1][0] - 1, i[1][1] - 1] in self.playerone and not [i[1][0] - 1, i[1][1] + 1] in self.playerone:
                    if not [i[1][0] + 1, i[1][1] - 1] in self.playerone and not [i[1][0] + 1, i[1][1] - 1] in self.kings or [i[1][0] + 1, i[1][1] + 1] in self.playerone and not [i[1][0] + 1, i[1][1] + 1] in self.kings:
                        self.moves_safe.append(i)
                    self.moves_safe.append(i)
            for i in self.playertwo:

                if [i[0]-2,i[1]-2] in self.playerone and not [i[0]-2,i[1]] in self.playerone:

                    if  [i[0],i[1]-2] in self.openspaces:
                        print("triggers here",[i, [i[0]-1,i[1]-1]] )
                        self.holes_exist.append([i, [i[0]-1,i[1]-1]])
                if [i[0]-2,i[1]+2] in self.playerone and not [i[0]-2,i[1]] in self.playerone:

                    if  [i[0], i[1] + 2] in self.openspaces:
                        print("no here",[i, [i[0]-1,i[1]+1]] )
                        self.holes_exist.append([i, [i[0]-1,i[1]+1]])
            self.moves_safe.extend(self.holes_exist)
            return ("safe moves",self.moves_safe)
    def jumps(self, who):
        def one_jumps(pieces, one_ahead, two_ahead):
            if who == self.playerone:
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

        if who == self.playertwo:
            one_jumps(self.playertwo, -1,-2)

        if who == self.playerone:
            one_jumps(self.playerone, 1,2)

        return (self.jumps_available)
    

    # safe_jumps does not account for kings. To determine if a jump is safe against a king, we will just have to check if a king has a jump in the opposite direction
    def safe_jumps(self, who):

        def free_jump(thejump, player):
            if player == "playerone":
                current_jump = thejump[0]
                for i in thejump[1]:

                    if i[1] - current_jump[1] > 0:
                        # this means if the jump is to the right
                        print("checking", [i[0] + 1, i[1] + 1])
                        if not [i[0] + 1, i[1] + 1] in self.playertwo and i[0] + 1 <=7:
                            if not [i[0] + 1, i[1] - 1] in self.playertwo:
                                if not [i[0] - 1, i[1] - 1] in self.playertwo and not [i[0] - 1,i[1] - 1] in self.kings or not [i[0] -1, i[1] + 1] in self.playertwo and not [i[0] - 1, i[1] + 1] in self.kings:
                                    print([i[0] + 1, i[1] - 1], "not in playertwo ye")
                                    safejump = thejump[1][:thejump[1].index(i) + 1]
                                    self.no_consequence_jump.append([thejump[0], safejump])
                            elif not [i[0] - 1, i[1] + 1] in self.openspaces:

                                print([i[0] - 1, i[1] + 1], "not in openspaces sd", self.openspaces)
                                safejump = thejump[1][:thejump[1].index(i) + 1]
                                self.no_consequence_jump.append([thejump[0], safejump])
                    else:
                        if not [i[0] + 1, i[1] - 1] in self.playertwo:
                            if not [i[0] +1 , i[1]  +1 ]  in self.playertwo:
                                if not [i[0] - 1, i[1] - 1] in self.playertwo and not [i[0] - 1,i[1] - 1] in self.kings or not [i[0] - 1,i[1] + 1] in self.playertwo and not [i[0] - 1,i[1] + 1] in self.kings:
                                    print([i[0] -1, i[1] + 1], "not in playertwo ba")
                                    safejump = thejump[1][:thejump[1].index(i) + 1]
                                    self.no_consequence_jump.append([thejump[0], safejump])
                            elif not [i[0] - 1, i[1] - 1] in self.openspaces:
                                print([i[0] - 1, i[1] - 1], "not in playertwo dv")
                                safejump = thejump[1][:thejump[1].index(i) + 1]
                                self.no_consequence_jump.append([thejump[0], safejump])
                    current_jump = i


            if player == "playertwo":
                current_jump = thejump[0]
                for i in thejump[1]:
                    if i[1] - current_jump[1] > 0:
                        # this means if the jump is to the right
                        print("checking", [i[0] - 1, i[1] + 1])
                        if not [i[0] - 1, i[1] + 1] in self.playertwo and i[0] + 1 <= 7:
                            if not [i[0] - 1, i[1] - 1] in self.playertwo:
                                if not [i[0] + 1, i[1] - 1] in self.playertwo and not [i[0] + 1,i[1] - 1] in self.kings or not [i[0] +1, i[1] + 1] in self.playertwo and not [i[0] + 1, i[1] + 1] in self.kings:
                                    print([i[0] - 1, i[1] - 1], "not in playertwo ye")
                                    safejump = thejump[1][:thejump[1].index(i) + 1]
                                    self.no_consequence_jump.append([thejump[0], safejump])
                            elif not [i[0] + 1, i[1] + 1] in self.openspaces:
                                print("this is also not in playertwo", [i[0] + 1, i[1] + 1])
                                print([i[0] + 1, i[1] + 1], "not in open space sd")
                                safejump = thejump[1][:thejump[1].index(i) + 1]
                                self.no_consequence_jump.append([thejump[0], safejump])
                    else:
                        if not [i[0] - 1, i[1] - 1] in self.playertwo:
                            if not [i[0] -1, i[1] + 1] in self.playertwo:
                                if not [i[0] + 1, i[1] - 1] in self.playertwo and not [i[0] + 1,i[1] - 1] in self.kings or not [i[0] +1, i[1] + 1] in self.playertwo and not [i[0] + 1, i[1] + 1] in self.kings:
                                    print([i[0] - 1, i[1] + 1], "not in playertwo ba")
                                    safejump = thejump[1][:thejump[1].index(i) + 1]
                                    self.no_consequence_jump.append([thejump[0], safejump])
                            elif not [i[0] + 1, i[1] - 1] in self.openspaces:
                                print([i[0] + 1, i[1] - 1], "not in playertwo dv")
                                safejump = thejump[1][:thejump[1].index(i) + 1]
                                self.no_consequence_jump.append([thejump[0], safejump])

        if who == self.playertwo:
            for i in self.jumps_available:
                free_jump(i, "playertwo")
            return ("these are the safe jumps", self.no_consequence_jump)

        if who == self.playerone:
            for i in self.jumps_available:
                free_jump(i, "playerone")
            return ("these are the safe jumps", self.no_consequence_jump)
    def moved(self, where, roomid):
        
        print("this is what where[1] is equal to", where[1])
        print("this is what where is equal to", where)
        where[1]=where[1][:where[1].index(where[1][-1])+1]
        

        self.roomid = roomid
        first_player = self.playerone
        

        
        the_game = Checkers.objects.get(roomid = roomid)
        kinged = ast.literal_eval(the_game.kings)
        
        # Figure out who's turn it is
        player_turn = the_game.team_owner.split()
        player_turns = len(player_turn)
        if player_turn.index(the_game.turn) < player_turns -1:
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
            first_player = self.playertwo
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
                print("appended", listy[i+1], "because last value is", last_value)
                newlist.append(listy[i+1])
                last_value = listy[i+1]
        where[1]=newlist[::-1]
        print("after changes, this is where[1]", where[1])
        temp_value = where[0]
        
        
        for i in where[1]:
            #here lies the problem. Jumped doesnt put the right thing for double jumps
            print(where, i, where[1])
            # the issue lies here for the second jump
            jumped = [int(abs(temp_value[0]+i[0])/2), int(abs(temp_value[1]+i[1])/2)]
            temp_value = i
            print("checker that was jumped", jumped)
            try:
                print(checker_removal)
                checker_delete =ast.literal_eval(checker_removal)
                checker_delete.remove(jumped)
                checker_delete = str(checker_delete)
                print("if it made it here, then Im stumped", checker_delete)
                checker_removal= checker_delete
                
                
            except:
                pass
        
        if player_turn.index(the_game.turn) < player_turns -1:

            the_game.player_one = checker_removal
        else:

            the_game.player_two = checker_removal
        
        the_game.save()
        print("__________________________________________________")

# Im gonna have to include jumps
def checkers_game(current_instance, moved=None):
    player_instance = current_instance.player_one
    team_owner = current_instance.team_owner.split()
    if team_owner.index(current_instance.turn) >0:

        player_instance = current_instance.player_two

    game_instance = Game(ast.literal_eval(current_instance.player_one), ast.literal_eval(current_instance.player_two), ast.literal_eval(current_instance.kings), current_instance.roomid)
    game_instance.available_moves(ast.literal_eval(player_instance))
    game_instance.in_danger(ast.literal_eval(player_instance))
    game_instance.safe_moves(ast.literal_eval(player_instance))
    game_instance.jumps(ast.literal_eval(player_instance))
    game_instance.safe_jumps(ast.literal_eval(player_instance))

    if current_instance.turn == "AI":
        
        print("we made it all the way here", player_instance)
        print("moves available",game_instance.moves_available)
        print("safe moves", game_instance.moves_safe)
        print("spots in danger", game_instance.pos_at_risk)
        print("safe jumps", game_instance.no_consequence_jump)
        print("jumps",game_instance.jumps_available )
        taskfulfilled = False
        # there are values in maxjump so that the if condition does not give an error
        maxjump = [[1,0],[[1,0]]]
        # priority one, make multi-jump
        if len(game_instance.jumps_available)>0:
            maxjump = max((x for x in game_instance.jumps_available))
        
        
        if len(maxjump[1])>1:
            print("AI made multi-jump")
            game_instance.moved(maxjump, current_instance.roomid)
        # priority two, get checkers out of risk
        elif len(game_instance.pos_at_risk) >0:
             
            for i in game_instance.pos_at_risk:
                # sub-priority one, perform safe jump with at risk checker if possible
                for j in game_instance.no_consequence_jump:
                    if i[0] == j[0]:
                        print("AI did a safe jump")
                        game_instance.moved(j, current_instance.roomid)
                        taskfulfilled = True
                        break
                if taskfulfilled == True:
                    break
                # sub-priority two, perform safe move with at risk checker if possible
                for k in game_instance.moves_safe:
                    if i[0] == k[0]:
                        print("AI did a safe move")
                        game_instance.moved([k[0],[k[1]]], current_instance.roomid)
                        taskfulfilled = True
                        break
                    # sub-priority three, cover at risk spot with another checker
                    if k[1] in i[1]:
                        print("AI did a block move")
                        game_instance.moved([k[0],[k[1]]], current_instance.roomid)
                        taskfulfilled = True
                        break
                if taskfulfilled == True:
                    break
        # priority three, make random safe move
        elif len(game_instance.moves_safe)>0:
            rand_num =len(game_instance.moves_safe)-1
            game_instance.moved([game_instance.moves_safe[rand_num][0],[game_instance.moves_safe[rand_num][1]]], current_instance.roomid)
        # priority four, make random jump
        elif len(game_instance.jumps_available)>0:
            rand_num =len(game_instance.jumps_available)-1
            game_instance.moved([game_instance.jumps_available[rand_num][0],[game_instance.jumps_available[rand_num][1]]], current_instance.roomid)
        # priority five, make random move
        else:
            rand_num =len(game_instance.moves_available)-1
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
        "available_space": game_instance.available_moves(ast.literal_eval(player_instance)), #at the moment we are only catering to player one
        "jumps": game_instance.jumps_available,
        "open_spaces": game_instance.openspaces ,
        "player_turn": current_instance.turn,

        }])





def dice_game():
    return 6