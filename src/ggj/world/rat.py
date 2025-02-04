import heapq
import logging
import random
import time

from typing_extensions import Callable, Optional

from ..drawing import shape as s
from ..events import Event, Events
from .gameobject import Collidable, GameObject, GameObjectUtils
from .manager import WorldManager
from .terrain import CROP_STAGES, Grass, Wheat

SURROUNDING_VECTOR = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]


def next_step(start: tuple[int, int], destination: tuple[int, int]) -> tuple[int, int]:
    """
    Perform greddy breadth first search to find the
    fast destination to the given path.
    Using the manhattan distance as the heuristic in the search.
    """
    frontier = [(0, start)]
    dest_x, dest_y = destination
    came_from: dict[tuple[int, int], tuple[int, int]] = dict()

    current = start

    while len(frontier):
        priority, current = heapq.heappop(frontier)
        curr_x, curr_y = current

        if current == destination:
            break

        for offset_x, offset_y in SURROUNDING_VECTOR:
            new_x, new_y = curr_x + offset_x, curr_y + offset_y

            if (new_x, new_y) in came_from:
                continue

            objs: list[GameObject] = WorldManager.get_objects(new_x, new_y)

            if next((o for o in objs if o.impassable()), None):
                continue

            priority = (abs(dest_x - new_x)) + (abs(dest_y - new_y))
            heapq.heappush(frontier, (priority, (new_x, new_y)))
            came_from[(new_x, new_y)] = current

    backtrack = current

    if not len(came_from):
        return destination

    if backtrack not in came_from:
        return start

    while came_from[backtrack] != start:
        backtrack = came_from[backtrack]

    return backtrack


STEP_INTERVAL = 0.5


class Rat(Collidable):
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.target_pos: Optional[tuple[int, int]]
        self._find_nearest_crop()
        self.last_step_time = 0
        self.on_out_of_sight: Optional[Callable[[set[str]], None]]

    def _find_nearest_crop(self):
        crops = WorldManager.get_objects_of_type(set(CROP_STAGES))
        crops.sort(key=lambda o: GameObjectUtils.distance(self, o))

        if not len(crops):
            self.target_pos = (self.pos[0], self.pos[1])
            return

        self.target_pos = crops[0].get_pos()

    def update(self):
        assert self.target_pos
        assert WorldManager.screen

        if (time.monotonic() - self.last_step_time) < STEP_INTERVAL:
            return

        self._find_nearest_crop()
        next_pos = next_step(self.get_pos(), self.target_pos)

        # TODO: have the rats moving away
        if self.target_pos == tuple(self.pos) and not len(
            WorldManager.get_objects_of_type(set(CROP_STAGES))
        ):
            WorldManager.remove(self)
            return

        WorldManager.remove(self)
        self.pos[0] = next_pos[0]
        self.pos[1] = next_pos[1]
        WorldManager.add_object(self)

        self.last_step_time = time.monotonic()

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "@", s.BLOOD_RED)

    def impassable(self) -> bool:
        return True

    def zindex(self) -> int:
        return -10

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def on_collide(self, object: GameObject):
        if isinstance(object, Wheat):
            x, y = self.get_pos()
            logging.debug("Eaten grass")
            WorldManager.clear_cell(x, y)
            WorldManager.add_object(Grass(x, y))


RAT_ATTACK_TIME = 30
START_RATS = 4


class RatOverseer:
    def __init__(self):
        self.on_rat_hidden: Callable[[set[str]], None] = lambda _: None
        self.on_all_rats: Callable[[], None] = lambda: None
        self.rat_attack_event: Events = Events([])
        self.num_rounds = 0

    def rat_attack(self):
        self.num_rounds += 1

        for _ in range(round(START_RATS * (self.num_rounds * 0.5))):
            grasses = WorldManager.get_objects_of_type({Grass})
            block = random.choice(grasses)
            WorldManager.add_object(Rat(*block.get_pos()))

    def _process_rat_attack(self):
        if not self.rat_attack_event.done():
            return

        if WorldManager.get_objects_of_type(set([Rat])):
            return

        target_objs = WorldManager.get_objects_of_type(set(CROP_STAGES))

        if not len(target_objs):
            return

        e = Event(RAT_ATTACK_TIME, self.rat_attack, False)
        self.rat_attack_event = Events([e])

    def update(self):
        assert WorldManager.screen
        self._process_rat_attack()
        self.rat_attack_event.check()
        out_of_sight = [
            o for o in WorldManager.get_out_of_sight_objects() if isinstance(o, Rat)
        ]

        if not len(out_of_sight):
            self.on_all_rats()
            return

        dirs: set[str] = set()

        for rat in out_of_sight:
            dirs = dirs | s.get_direction(WorldManager.screen, *rat.get_pos())

        self.on_rat_hidden(dirs)

    def draw(self):
        pass

    def impassable(self) -> bool:
        return True

    def zindex(self) -> int:
        return 1000

    def get_pos(self) -> tuple[int, int]:
        return (1000, 1000)

    def set_on_all_rats(self, c: Callable[[], None]):
        self.on_all_rats = c

    def set_on_rat_hidden(self, c: Callable[[set[str]], None]):
        self.on_rat_hidden = c
