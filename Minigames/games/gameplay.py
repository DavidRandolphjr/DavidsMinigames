from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import Room, Checkers, Dice, Lobby
from .models import User
import ast

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
    def safe_moves(self, who):
        if who == self.playerone:
            for i in self.moves_available:
                #check to see if spot ahead of moves_available is open.
                if not [i[1][0] + 1, i[1][1] - 1] in self.playertwo and not [i[1][0] + 1, i[1][1] + 1] in self.playertwo:
                    self.moves_safe.append(i)
            for i in self.playerone:

                if [i[0]+2,i[1]-2] in self.playertwo and not [i[0]+2,i[1]] in self.playertwo:

                    if not [i[0],i[1]-2] in self.openspaces:
                        self.holes_exist.append([i, [i[0]+1,i[1]-1]])
                if [i[0]+2,i[1]+2] in self.playertwo and not [i[0]+2,i[1]] in self.playertwo:

                    if not [i[0], i[1] + 2] in self.openspaces:
                        self.holes_exist.append([i, [i[0]+1,i[1]+1]])
            self.moves_safe.extend(self.holes_exist)
            return ("safe moves",self.moves_safe)

        if who == self.playertwo:
            for i in self.moves_available:
                #check to see if spot ahead of moves_available is open.
                if not [i[1][0] - 1, i[1][1] - 1] in self.playerone and not [i[1][0] - 1, i[1][1] + 1] in self.playertwo:
                    self.moves_safe.append(i)
            for i in self.playertwo:

                if [i[0]-2,i[1]-2] in self.playerone and not [i[0]-2,i[1]] in self.playerone:

                    if not [i[0],i[1]-2] in self.openspaces:
                        self.holes_exist.append([i, [i[0]-1,i[1]-1]])
                if [i[0]-2,i[1]+2] in self.playerone and not [i[0]-2,i[1]] in self.playerone:

                    if not [i[0], i[1] + 2] in self.openspaces:
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
                print("this is i and self.kings ", i, self.kings)

                self.jumps = []
                if [i[0]+one_ahead, i[1]+1] in oposer and [i[0]+two_ahead, i[1]+2] in self.openspaces:
                    self.jumps.append([i[0]+two_ahead, i[1]+2])

                    for j in self.jumps:

                        if [j[0]+one_ahead, j[1]+1] in oposer and [j[0]+two_ahead, j[1]+2] in self.openspaces:
                            self.jumps.append([j[0]+two_ahead, j[1]+2])
                        if [j[0] + one_ahead, j[1] - 1] in oposer and [j[0] + two_ahead, j[1] - 2] in self.openspaces:

                            self.jumps.append([j[0] + two_ahead, j[1] - 2])
                print("these are the jumps available",[i, self.jumps] )
                self.jumps_available.append([i, self.jumps])
                self.jumps = []
                if [i[0]+one_ahead, i[1]-1] in oposer and [i[0]+two_ahead, i[1]-2] in self.openspaces:
                    self.jumps.append([i[0]+two_ahead, i[1]-2])
                    for j in self.jumps:

                        if [j[0]+one_ahead, j[1]+1] in oposer and [j[0]+two_ahead, j[1]+2] in self.openspaces:
                            self.jumps.append([j[0]+two_ahead, j[1]+2])
                        if [j[0] + one_ahead, j[1] - 1] in oposer and [j[0] + two_ahead, j[1] - 2] in self.openspaces:

                            self.jumps.append([j[0] + two_ahead, j[1] - 2])
                print("these are the jumps available",[i, self.jumps] )
                self.jumps_available.append([i, self.jumps])
                if i in self.kings and [i] != pieces:
                    one_jumps([i], one_ahead*-1,two_ahead*-1)

        if who == self.playertwo:
            one_jumps(self.playertwo, -1,-2)

        if who == self.playerone:
            one_jumps(self.playerone, 1,2)

        return (self.jumps_available)
    
    def moved(self, where, roomid):


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
        

        
        temp_value = where[0]
        print("this is where", where)
        
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
        print("this is checker removal", checker_removal)
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
    if moved:

        game_instance.moved(moved, current_instance.roomid)
    return ([{
        "player_one": ast.literal_eval(current_instance.player_one), 
        "player_two": ast.literal_eval(current_instance.player_two), 
        "kings": ast.literal_eval(current_instance.kings),
        "available_space": game_instance.available_moves(ast.literal_eval(player_instance)), #at the moment we are only catering to player one
        "jumps": game_instance.jumps(ast.literal_eval(player_instance)),
        "open_spaces": game_instance.openspaces ,
        "player_turn": current_instance.turn,
        }])





def dice_game():
    return 6