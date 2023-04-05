from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("games", views.index, name="index"),
    path("notfound", views.notfound, name="notfound"),
    path("game/<str:gamename>/<int:id>/<str:name>/", views.game, name="game"),
    path("started/<int:id>", views.started, name="started"),
    path("board/<int:id>", views.board, name="board"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
]