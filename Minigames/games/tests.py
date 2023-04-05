from django.test import TestCase
from gameplay import checkers_game, Game
import ast
# Create your tests here.


bob=Game([[0,0],[0,2],[0,4],[0,6],[1,1],[1,3],[1,5],[1,7],[2,0],[2,2],[2,4],[2,6]],[[7,1],[7,3],[7,5],[7,7],[6,0],[6,2],[6,4],[6,6],[5,1],[5,3],[5,5],[5,7]])
print(bob.jumps([[7,1],[7,3],[7,5],[7,7],[6,0],[6,2],[6,4],[6,6],[5,1],[5,3],[5,5],[5,7]]))