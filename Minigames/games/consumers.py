import json
import random
import ast
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from .models import Room, Checkers
from .gameplay import checkers_game, Game


class MyConsumer(WebsocketConsumer):
    
    def connect(self):
        self.room_group_name = 'test'
        
    
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        print("we are in the starter area")

        self.accept()
        self.send(text_data=json.dumps({
            'type':'firstload',
            'message':"doesnt go anywhere"
            #This can just send out the initial list
        }))
        

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
       
        name = text_data_json['name']
        roomid = text_data_json['roomid']
        room = Room.objects.get(pk=roomid)
        library = {
                    "Checkers": Checkers.objects.get(roomid=roomid), 
                    #"Dice":dice
                    }
        try:
            # Even though start_game isnt being used, I think it makes this statement work because try: would stop if it didnt recieve "started"
            start_game = text_data_json['started']
            team_one = text_data_json['team_one']
            team_two = text_data_json['team_two']
            print("we have made it to here")
            
            #dice = Dice.objects.get(roomid=room)
            
            library[room.gamename].started = True
            library[room.gamename].team_owner = str(team_one)+ " " +str(team_two)
            player_turn = library[room.gamename].team_owner.split()
            library[room.gamename].turn = player_turn[0]
            print("we made it this far as well")
            library[room.gamename].save()
            # not sure if we need to send 'team_owners', but we will for now
            return(async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'game_message',
                'team_owners': library[room.gamename].team_owner.split(),
                'roomid': roomid
            }
            ))
        except:
            pass
        
        # I think this is the part where we add game functions from another file. We have to create them, but I am thinking this is where we start the unique game functions
        # If 

        

        #
        try:
            # once we implement turns, we are going to have to specify here who made what move. I think we can just ask the instance's database for the turn. such as Checkers.objects.get(roomid=roomid).turn
            # While this current solution works, I am thinking that we redo this so that gameplay.py handles this. I think that makes this more readable, but could also simplify things.
            # I think we should use games_start to do it.
            moved= None
            games_start = {
                "Checkers": checkers_game,
                #"Dice":dice
            }
            moved = text_data_json['moved']
            
            print("this is the move", moved)

            games_start[room.gamename](library[room.gamename], moved)

            return(async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'game_message',
                'team_owners': moved,
                'roomid': roomid
                
            }))
        except:
            pass
        try:
            # once we implement turns, we are going to have to specify here who made what move. I think we can just ask the instance's database for the turn. such as Checkers.objects.get(roomid=roomid).turn
            # While this current solution works, I am thinking that we redo this so that gameplay.py handles this. I think that makes this more readable, but could also simplify things.
            # I think we should use games_start to do it.
            
            games_start = {
                "Checkers": checkers_game,
                #"Dice":dice
            }
            AIturn = text_data_json['AIturn']
            
            print("Its AI time", AIturn)

            games_start[room.gamename](library[room.gamename])

            return(async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'game_message',
                'team_owners': moved,
                'roomid': roomid
                
            }))
        except:
            pass
        print("this could be a problem if this is triggering every time")
        # I am thinking we can let this be the final function
        if library[room.gamename].started == False:
            print("its getting in here for some reason")
            if roomid and len(text_data_json) <=2:
                team_owners = library[room.gamename].team_owner
                if not name in team_owners:
                    team_owners += " %s" %(name)
                    library[room.gamename].team_owner= team_owners
                    library[room.gamename].save()
                
                return(async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type':'game_message',
                    'team_owners': team_owners.split(),
                    'roomid': roomid
                    
                }
            ))
        # we can pass a list by doing team_owners.split()

        # this is essentially here to just get the user to interact with the page

        

    def game_message(self, event):
        team_owners = event['team_owners']
        roomid = event['roomid']


        self.send(text_data=json.dumps({
            'type':roomid,
            'team_owners': team_owners,
            'roomid': roomid

        }))


# I am thinking that we make it so that whenever a person is at a game link, they join the lobby. I think that can be done already by adding name to Checkers.lobby
# However, we will likely have to pass the roomid if we go that route. Perhaps we can make things easier by passing info from url.


