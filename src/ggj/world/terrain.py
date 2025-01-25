from typing_extensions import Dict, Callable
from curses import window
from ..drawing import shape as s
from .manager import WorldManager
from .gameobject import GameObject
import logging

class Grass:
    def __init__(self, x: int, y: int, win: window):
        self.window = win
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        x, y = self.pos
        s.world_char(self.window, x, y, ';', s.GREEN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return False

class Boundary:
    def __init__(self, x: int, y: int, win: window):
        self.window = win
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        x, y = self.pos
        s.world_char(self.window, x, y, '♠', s.DARK_GREEN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True

class Water:
    def __init__(self, x: int, y: int, win: window):
        self.window = win
        self.pos = [x, y]

    def update(self):
        pass

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def draw(self):
        x, y = self.pos
        s.world_char(self.window, x, y, '~', s.DEEP_BLUE)

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True

class TerrainFactory:
    @staticmethod
    def create_terrain(world: list[list[str]], win: window):
        terrain_map: Dict[str, Callable[[int, int, window], GameObject]] = {
            ';': Grass,
            '♠': Boundary,
            '~': Water,
        }

        for y, row in enumerate(world):
            for x, cell in enumerate(row):
                if cell not in terrain_map:
                    raise Exception ("terrain tile does not exist")

                obj: GameObject = terrain_map[cell](x, y, win)
                logging.debug(obj)
                WorldManager.add_object(obj)
