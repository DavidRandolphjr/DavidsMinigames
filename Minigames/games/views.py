import json
import time
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import os
from .models import Room, Checkers, Dice, Lobby
from .gameplay import checkers_game, Game

from .models import User

# Create your views here.

@csrf_exempt
@login_required
def index(request):

    
    games = [
        "Checkers",
        "Uno"
        ]
    images = [
        "/games/files/userimages/Checkerboard-draughtboard-play.webp", #Checkers
        "jim", #Uno
        ]
    length=range(len(games))
    #The purpose of games_id and games_string is to pass them to the url for each game in order to create a new instance..
    games_id= 0
    games_string = "empty"

    return render(request, "games/index.html",{"games": games, "images":images, "length": length, "games_id": games_id, "games_string": games_string})

def game(request, gamename=None ,id=None, name=None):
    #the idea is that this first part will only trigger when a room is already created. If someone visits an existing link then this will work

    if id and name != "empty":
        try:
            # i can create another library dictionary that changes the html that the user gets redirected to
            room = Room.objects.get(id=id, name=name)
            return render(request, "games/game.html", {"room": room.id, "name": request.user, "gamename": gamename})
        except Room.DoesNotExist:

            #messages.error(request, "Room does not exist. You fool!!")
            return redirect("notfound")
    else:
        room = Room(
            name = request.user,
            gamename = gamename)
        room.save()
        #game library

        dice = Dice(
            roomid= Room.objects.get(pk = room.id)
        )
        lobby = Lobby(
            roomid= Room.objects.get(pk = room.id),
            players = request.user
        )
        library = {
            "Checkers": Checkers(
            roomid= Room.objects.get(pk = room.id),
            team_owner= "AI %s" % (request.user)
            ), 
            "Dice":dice
            }

        #create class instance based on gamename
        lobby.save()
        library[gamename].save()
        library[gamename].lobby.add(lobby)
        
        return redirect('game', gamename=gamename, id=room.id, name=request.user)

def started(request, id):
    room = Room.objects.get(pk=id)
    #dice = Dice.objects.get(roomid=room)
    library = {
            "Checkers": Checkers.objects.get(roomid=id), 
            #"Dice":dice
            }
    #library[room.gamename].started = True
    library[room.gamename].save()
    return JsonResponse(library[room.gamename].started, safe=False)
# we have to make a start button elsewhere

def board(request, id):
    room = Room.objects.get(pk=id)
    #dice = Dice.objects.get(roomid=room)
    library = {
            "Checkers": Checkers.objects.get(roomid=id), 
            #"Dice":dice
            }
    game_instance = library[room.gamename]
    game_board = {
            "Checkers": checkers_game(game_instance), 
            #"Dice":dice
            }
    

    # I think we should then pass game_instance to the proper function in gameplay.py
    return JsonResponse(game_board[room.gamename], safe=False)

    
def notfound(request):
    return render(request, "games/notfound.html")



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "games/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "games/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "Drafter/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "games/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "games/register.html")