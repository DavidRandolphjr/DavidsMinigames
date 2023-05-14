from email.policy import default
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _


class User(AbstractUser):
    pass

class Room(models.Model):
    name = models.CharField(max_length=500)
    gamename = models.CharField(max_length=500)
    def __str__(self) -> str:
        return f"{self.id} name: {self.name}"

class Lobby(models.Model):
    roomid = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="lobbyroomid", null=True)
    players = models.CharField(max_length=500)

# we have to add who's turn it is
class Checkers(models.Model):
    #roomid is what is going to link the Checkers class to the room class
    roomid = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="checkerroomid", null=True)
    lobby = models.ManyToManyField("Lobby", related_name="players_in_lobby")
    # We can prompt the user to choose a team. Then it will go to views.py or consumers.py and change team_owner to something like [David,AI]
    team_owner = models.CharField(max_length=500, default="AI")
    player_one = models.CharField(max_length=500, default="[[0,0],[0,2],[0,4],[0,6],[1,1],[1,3],[1,5],[1,7],[2,0],[2,2],[2,4],[2,6]]")
    player_two = models.CharField(max_length=500, default="[[7,1],[7,3],[7,5],[7,7],[6,0],[6,2],[6,4],[6,6],[5,1],[5,3],[5,5],[5,7]]")
    openspaces = models.CharField(max_length=500, default="[[3,1],[3,3],[3,5],[3,7],[4,0],[4,2],[4,4],[4,6]]")
    kings = models.CharField(max_length=500, default="[]")
    started = models.BooleanField(default=False)
    turn = models.CharField(max_length=500, default="AI")
    def __str__(self) -> str:
        return f""
    
class Monopoly(models.Model):
    #roomid is what is going to link the Dice class to the room class
    roomid = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="monopolyroomid", null=True)
    lobby = models.ManyToManyField("Lobby", related_name="people_in_lobby")
    # We can prompt the user to choose a team. Then it will go to views.py or consumers.py and change team_owner to something like [David,AI]
    team_owner = models.CharField(max_length=500, default="AI")
    positions = models.CharField(max_length=500, default="[0,0,0,0]")
    monopolies = models.CharField(max_length=500, default="[]")
    money = models.CharField(max_length=500, default="[1500,1500,1500,1500]")
    # player_one,two,three,four will contain the properties that are owned.
    player_one = models.CharField(max_length=500, default="[]")
    player_two = models.CharField(max_length=500, default="[]")
    player_three = models.CharField(max_length=500, default="[]")
    player_four = models.CharField(max_length=500, default="[]")
    rolled_dice = models.BooleanField(default=False)
    
    started = models.BooleanField(default=False)
    turn = models.CharField(max_length=500, default="AI")
    def __str__(self) -> str:
        return f""