from typing_extensions import Dict, Callable
from curses import window
from ..drawing import shape as s
from .manager import WorldManager
from .gameobject import GameObject
import logging
import random

class Grass:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.colour = s.GREEN if random.random() < 0.85 else s.DEEP_GREEN

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, ';', self.colour)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return False

class Boundary:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, '♠', s.DARK_GREEN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True

class Water:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def update(self):
        pass

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, '~', s.DEEP_BLUE)

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True

class Soil:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, '!', s.LIGHT_BROWN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True

class PlantedSoil:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, '`', s.LIGHT_YELLOW)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True

class Wheat:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, '$', s.GOLDEN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True

class Hole:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, 'O', s.MAROON)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return False

class TerrainFactory:
    @staticmethod
    def create_terrain(world: list[list[str]]):
        terrain_map: Dict[str, Callable[[int, int], GameObject]] = {
            ';': Grass,
            '♠': Boundary,
            '~': Water,
            '!': Soil,
            '^': PlantedSoil,
            '$': Wheat,
        }

        for y, row in enumerate(world):
            for x, cell in enumerate(row):
                if cell not in terrain_map:
                    raise Exception ("terrain tile does not exist")

                obj: GameObject = terrain_map[cell](x, y)
                logging.debug(obj)
                WorldManager.add_object(obj)
