import random
from typing import Callable, Dict, Optional

from ggj.drawing import shape as s
from ggj.util.constants import SURROUNDING_VECTOR
from ggj.util.events import Event, Events
from ggj.world.gameobject import GameObject
from ggj.world.manager import WorldManager


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
        self.last_spill_event: Events = Events(
            [Event(SPILL_INTERVAL, self._fill_water)]
        )

    def update(self):
        self.last_spill_event.check()

    def _fill_water(self):
        pos_x, pos_y = self.pos

        for vec_x, vec_y in SURROUNDING_VECTOR:
            n_x, n_y = pos_x + vec_x, pos_y + vec_y
            objs = WorldManager.get_objects(n_x, n_y)

            is_water = any(filter(lambda o: isinstance(o, Water), objs))

            if is_water:
                WorldManager.clear_cell(pos_x, pos_y)
                WorldManager.add_object(Water(pos_x, pos_y))

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
        self.glisten_event: Optional[Events] = None
        self.colour = s.GLISTEN_BLUE if random.uniform(0, 1) < 0.25 else s.DEEP_BLUE
        self._on_glisten()

    def update(self):
        assert self.glisten_event
        self.glisten_event.check()

    def _on_glisten(self):
        self.colour = s.GLISTEN_BLUE if random.uniform(0, 1) < 0.5 else s.DEEP_BLUE
        self.glisten_event = Events(
            [Event(random.uniform(1, MAX_GLISTEN_INTERVAL), self._on_glisten)]
        )

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


WHEAT_TIME = 20


class PlantedSoil:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.wheat_event = Events([Event(WHEAT_TIME, self._transform_to_wheat)])

    def update(self):
        self.wheat_event.check()

    def _transform_to_wheat(self):
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


CROP_STAGES = [PlantedSoil, Wheat]
