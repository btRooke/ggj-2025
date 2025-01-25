from typing_extensions import Dict, Callable
from ..drawing import shape as s
from .manager import WorldManager
from .gameobject import GameObject

# from .player import Player
import random
import time


class Grass:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.colour = s.GREEN if random.random() < 0.85 else s.DEEP_GREEN

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

    def update(self):
        pass

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


class Water:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.last_spill_time = 0

    def update(self):
        pos_x, pos_y = self.get_pos()

        if (time.monotonic() - self.last_spill_time) < SPILL_INTERVAL:
            return

        # if cell next to current cell is a hole then replace the cel
        # with water after x number of seconds
        surrounding_vector = [
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ]

        for vec_x, vec_y in surrounding_vector:
            n_x, n_y = pos_x + vec_x, pos_y + vec_y
            objs = WorldManager.get_objects(n_x, n_y)

            is_hole = any(filter(lambda o: isinstance(o, Hole), objs))
            # is_player = any(filter(lambda o: isinstance(o, Player), objs)) TODO eek fix circular import

            if is_hole:  #  and not is_player:
                WorldManager.clear_cell(n_x, n_y)
                WorldManager.add_object(Water(n_x, n_y))

        self.last_spill_time = time.monotonic()

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "~", s.DEEP_BLUE)

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
        return True


class PlantedSoil:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "`", s.LIGHT_YELLOW)

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
        s.world_char(WorldManager.screen, x, y, "$", s.GOLDEN)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return 0

    def impassable(self) -> bool:
        return True


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
        }

        for y, row in enumerate(world):
            for x, cell in enumerate(row):
                if cell not in terrain_map:
                    raise Exception("terrain tile does not exist")

                obj: GameObject = terrain_map[cell](x, y)
                WorldManager.add_object(obj)
