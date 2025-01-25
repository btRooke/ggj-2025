from curses import window
from .gameobject import Wiedable
from .player import Player
from .manager import WorldManager
from .terrain import Hole

class Shovel(Wiedable):
    def __init__(self, p: Player):
        self.player = p

    def execute(self):
        x, y = self.player.get_pos()
        WorldManager.clear_cell(x, y)
        WorldManager.add_object(Hole(x, y))
