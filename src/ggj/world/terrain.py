from typing_extensions import Dict, Callable
from ..drawing import shape as s
from .manager import WorldManager
from .gameobject import GameObject
import random
import time

SURROUNDING_VECTOR = [ (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1),
                      (0, 1), (1, 1), ]

class Grass:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.colour = s.GREEN if random.uniform(0, 1) < 0.85 else s.DEEP_GREEN

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, ";", self.colour)

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
        s.world_char(WorldManager.screen, x, y, "♠", s.DARK_GREEN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True

class Hole:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.last_spill_time = 0

    def update(self):
        pos_x, pos_y = self.pos

        self.last_spill_time = time.monotonic() if self.last_spill_time == 0 \
                else self.last_spill_time

        if (time.monotonic() - self.last_spill_time) < SPILL_INTERVAL:
            return

        # if cell next to current cell is a hole then replace the cel
        # with water after x number of seconds
        for vec_x, vec_y in SURROUNDING_VECTOR:
            n_x, n_y = pos_x + vec_x, pos_y + vec_y
            objs = WorldManager.get_objects(n_x, n_y)

            is_water = any(filter(lambda o: isinstance(o, Water), objs))

            if is_water:
                WorldManager.clear_cell(pos_x, pos_y)
                WorldManager.add_object(Water(pos_x, pos_y))

        self.last_spill_time = time.monotonic()


    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "O", s.MAROON)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return False


SPILL_INTERVAL = 2
MAX_GLISTEN_INTERVAL = 5

class Water:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.last_glisten_time = 0
        self.colour = s.GLISTEN_BLUE if random.uniform(0, 1) < 0.25 else s.DEEP_BLUE

    def update(self):
        if (time.monotonic() - self.last_glisten_time) > random.uniform(1, MAX_GLISTEN_INTERVAL):
            self.colour = s.GLISTEN_BLUE if random.uniform(0, 1) < 0.5 else s.DEEP_BLUE
            self.last_glisten_time = time.monotonic()

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "~", self.colour)

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
        s.world_char(WorldManager.screen, x, y, "!", s.LIGHT_BROWN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return False

WHEAT_TIME = 5

class PlantedSoil:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.creation_time = time.monotonic()

    def update(self):
        if (time.monotonic() - self.creation_time) < WHEAT_TIME:
            return

        pos_x, pos_y = self.get_pos()
        WorldManager.clear_cell(pos_x, pos_y)
        WorldManager.add_object(Wheat(pos_x, pos_y))

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "`", s.LIGHT_YELLOW)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return False

class Wheat:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "$", s.GOLDEN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return False

class Scarecrow:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def _place_spikes(self):
        pass

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "¥", s.PURPLE)

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
            ";": Grass,
            "♠": Boundary,
            "~": Water,
            "!": Soil,
            "^": PlantedSoil,
            "$": Wheat,
            "¥": Scarecrow,
        }

        for y, row in enumerate(world):
            for x, cell in enumerate(row):
                if cell not in terrain_map:
                    raise Exception("terrain tile does not exist")

                obj: GameObject = terrain_map[cell](x, y)
                WorldManager.add_object(obj)
