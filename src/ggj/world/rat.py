from typing_extensions import Optional
import heapq
import time
from .manager import WorldManager
from .terrain import Wheat, PlantedSoil
from ..drawing import shape as s
from .gameobject import GameObject, GameObjectUtils
import logging

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

    def _find_nearest_crop(self):
        crops = WorldManager.get_objects_by_pred({ Wheat, PlantedSoil })
        crops.sort(key=lambda o: GameObjectUtils.distance(self, o))

        if not len(crops):
            self.target_pos = (self.pos[0], self.pos[1])
            logging.debug("No crops founds")
            return

        self.target_pos = crops[0].get_pos()
        logging.debug(f"Set targetpos: f{self.target_pos}")

    def update(self):
        assert self.target_pos

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
