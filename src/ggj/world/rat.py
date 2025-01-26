from typing_extensions import Optional, Callable
import heapq
import time
from .manager import WorldManager
from .terrain import Wheat, PlantedSoil
from ..drawing import shape as s
from .gameobject import GameObject, GameObjectUtils
import logging
from .camera import Camera

SURROUNDING_VECTOR = [ (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1),
                      (0, 1), (1, 1), ]

def next_step(start: tuple[int, int], destination: tuple[int, int]) -> tuple[int, int]:
    """
    Perform greddy breadth first search to find the
    fast destination to the given path.
    Using the manhattan distance as the heuristic in the search.
    """
    frontier = [(0, start)]
    dest_x, dest_y = destination
    came_from: dict[tuple[int, int], tuple[int, int]] = dict()

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

    backtrack = destination

    if not len(came_from):
        return destination

    while came_from[backtrack] != start:
        backtrack = came_from[backtrack]

    return backtrack

STEP_INTERVAL = .5

class Rat:
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.target_pos: Optional[tuple[int, int]]
        self._find_nearest_crop()
        self.last_step_time = 0
        self.on_out_of_sight: Optional[Callable[[set[str]], None]]

    def _find_nearest_crop(self):
        crops = WorldManager.get_objects_of_type({ Wheat, PlantedSoil })
        crops.sort(key=lambda o: GameObjectUtils.distance(self, o))

        if not len(crops):
            self.target_pos = (self.pos[0], self.pos[1])
            logging.debug("No crops founds")
            return

        self.target_pos = crops[0].get_pos()
        logging.debug(f"Set targetpos: f{self.target_pos}")

    def update(self):
        assert self.target_pos
        assert WorldManager.screen

        if (time.monotonic() - self.last_step_time) < STEP_INTERVAL:
            return

        self._find_nearest_crop()
        next_pos = next_step(self.get_pos(), self.target_pos)

        self.pos[0] = next_pos[0]
        self.pos[1] = next_pos[1]

        logging.debug(f"Moving to: f{self.pos}")

        self.last_step_time = time.monotonic()

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, '@', s.BLOOD_RED)

    def impassable(self) -> bool:
        return True

    def zindex(self) -> int:
        return -10

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

class RatOverseer:
    def __init__(self):
        self.on_rat_hidden: Callable[[set[str]], None] = lambda _: None
        self.on_all_rats: Callable[[], None] = lambda: None

    def _get_rat_direction(self, r: Rat) -> set[str]:
        assert WorldManager.screen
        r_x, r_y = r.get_pos()
        c_x, c_y = Camera.get_pos()

        viewport, _ = WorldManager.screen.getmaxyx()

        top_cam_y = c_y - viewport / 2
        bottom_cam_y = c_y + viewport / 2
        left_cam_x = c_x - viewport / 2
        right_cam_x = c_x + viewport / 2

        directions: set[str] = set()

        if r_y < top_cam_y:
            directions.add('n')

        if r_y > bottom_cam_y:
            directions.add('s')

        if r_x < left_cam_x:
            directions.add('w')

        if r_x > right_cam_x:
            directions.add('e')

        return directions

    def update(self):
        out_of_sight = (o for o in WorldManager.get_out_of_sight_objects() if isinstance(o, Rat))

        if not next(out_of_sight, None):
            self.on_all_rats()
            return

        dirs: set[str] = set()

        for rat in out_of_sight:
            dirs = dirs | self._get_rat_direction(rat)

        self.on_rat_hidden(dirs)

    def draw(self):
        pass

    def impassable(self) -> bool:
        return True

    def zindex(self) -> int:
        return 1000

    def get_pos(self) -> tuple[int, int]:
        return (0, 0)

    def set_on_all_rats(self, c: Callable[[], None]):
        self.on_all_rats = c

    def set_on_rat_hidden(self, c: Callable[[set[str]], None]):
        self.on_rat_hidden = c
