import curses
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Optional, Callable
from .camera import Camera
from .gameobject import GameObject, Collidable
from .item import Item, SHOVEL, WOODEN_STICK, SEEDS, SCYTHE, WHEAT
from .manager import WorldManager
from .rat import Rat
from .terrain import (
    Hole,
    Soil,
    Water,
    PlantedSoil,
    Wheat,
    Grass,
    SURROUNDING_VECTOR,
)
from ..drawing import shape as s

MOVE_CAMERA_COLS = 5
logger = logging.getLogger(__name__)


@dataclass
class PlayerInventory:
    inventory: dict[Item, int] = field(default_factory=dict)
    active_item: Optional[Item] = None
    update_inv_cb: Optional[Callable[[], None]] = None

    def next_active(self) -> None:
        items: list[Item] = sorted(
            filter(lambda i: "wieldable" in i.traits, self.inventory),
            key=lambda x: x.name,
        )
        if self.active_item is None:
            if len(items) == 0:
                return
            else:
                self.active_item = items[0]
                return
        current_index = None
        for i in range(len(items)):
            if items[i].name == self.active_item.name:
                current_index = i
                break
        assert current_index is not None
        next_item_name = items[(current_index + 1) % len(items)].name
        next_item = [i for i in self.inventory if i.name == next_item_name]
        assert len(next_item) == 1
        logger.info(f"switching to {next_item}")
        self.active_item = next_item[0]

        if self.update_inv_cb:
            self.update_inv_cb()

    def pickup(self, item: Item, amount: int):
        a = self.inventory.get(item, 0)
        self.inventory[item] = a + amount

        if self.update_inv_cb:
            self.update_inv_cb()

    def remove(self, item: Item):
        number = self.inventory.get(item, 0) - 1

        if number <= 0:
            items: list[Item] = sorted(self.inventory, key=lambda x: x.name)
            assert len(items) > 1 and item in items
            item_idx = items.index(item)
            self.inventory.pop(item)
            self.active_item = items[(item_idx + 1) % len(items)]
        else:
            self.inventory[item] = number

        if self.update_inv_cb:
            self.update_inv_cb()


class Player(Collidable):
    def __init__(self, x: int, y: int):
        self.pos: list[int] = [x, y]

        # inventory
        self.inventory = PlayerInventory()
        self.inventory.inventory[SHOVEL] = 1
        self.inventory.inventory[WOODEN_STICK] = 1
        self.inventory.inventory[SEEDS] = 5
        self.inventory.inventory[SCYTHE] = 1
        self.inventory.active_item = SHOVEL

        # whack animation
        self._whack_animation_start: Optional[float] = None

        # item actions
        self.item_actions = {
            SHOVEL: self.dig,
            SEEDS: self.place,
            SCYTHE: self.cultivate,
            WOODEN_STICK: self.whack,
        }

    def update(self):

        # whack animation disable after a while

        if (
            self._whack_animation_start is not None
            and time.monotonic() - self._whack_animation_start > 0.25
        ):
            self._whack_animation_start = None

    def whack(self):
        self._trigger_whack_animation()
        rats = list(
            filter(
                lambda o: isinstance(o, Rat)
                and o.get_pos() in self.get_surrounding(),
                WorldManager.objects,
            )
        )
        for rat in rats:
            WorldManager.objects.remove(rat)

    def dig(self):
        x, y = self.get_pos()
        WorldManager.clear_cell(x, y)
        WorldManager.add_object(Hole(x, y))

    def place(self):
        x, y = self.get_pos()
        objs = WorldManager.get_objects(x, y)

        if not any(filter(lambda o: isinstance(o, Soil), objs)):
            return

        WorldManager.clear_cell(x, y)
        WorldManager.add_object(PlantedSoil(x, y))
        self.inventory.remove(SEEDS)

    def cultivate(self):
        pos_x, pos_y = self.get_pos()

        objs = WorldManager.get_objects(pos_x, pos_y)

        if any(filter(lambda o: isinstance(o, Wheat), objs)):
            return self._harvest_wheat()

        return self._till_soil()

    def _harvest_wheat(self):
        pos_x, pos_y = self.get_pos()
        WorldManager.clear_cell(pos_x, pos_y)
        WorldManager.add_object(Grass(pos_x, pos_y))
        self.inventory.pickup(SEEDS, random.randint(1, 3))
        self.inventory.pickup(WHEAT, 1)

    def _till_soil(self):
        pos_x, pos_y = self.get_pos()

        # can only place is near a water tile
        surrounding_vectors = {
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        }

        surrounding_objs = []

        for vec_x, vec_y in surrounding_vectors:
            n_x, n_y = pos_x + vec_x, pos_y + vec_y
            objs = WorldManager.get_objects(n_x, n_y)
            surrounding_objs.extend(objs)

        if not any(filter(lambda o: isinstance(o, Water), surrounding_objs)):
            return

        WorldManager.clear_cell(pos_x, pos_y)
        WorldManager.add_object(Soil(pos_x, pos_y))

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "#", s.DARK_RED)
        if self._whack_animation_start is not None:
            s.world_char(WorldManager.screen, x, y, "X", curses.A_BLINK)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def get_surrounding(self) -> tuple[tuple[int, int]]:
        pj, pi = self.get_pos()
        return tuple((sj + pj, si + pi) for (si, sj) in SURROUNDING_VECTOR)  # type: ignore

    def zindex(self) -> int:
        return -10

    def move(self, move_vector: tuple[int, int]):
        x, y = move_vector

        new_pos_x = self.pos[0] + x
        new_pos_y = self.pos[1] + y

        if not WorldManager.can_place(new_pos_x, new_pos_y):
            curses.beep()
            return

        self.pos[0] = new_pos_x
        self.pos[1] = new_pos_y

        player_x, player_y = self.get_pos()
        cam_x, cam_y = Camera.get_pos()

        x_exceeded = abs(cam_x - player_x) >= MOVE_CAMERA_COLS
        y_exceeded = abs(cam_y - player_y) >= MOVE_CAMERA_COLS

        # determine if player exceeds bounding box. Move camra if player
        # out of bounding box
        if x_exceeded or y_exceeded:
            Camera.move_camera(move_vector)

    def impassable(self) -> bool:
        return True

    def on_collide(self, object: GameObject):
        pass

    def execute(self):
        if (
            self.inventory.active_item
            and self.inventory.active_item in self.item_actions
        ):
            assert (
                self.inventory.active_item in self.inventory.inventory
                and self.inventory.inventory[self.inventory.active_item] > 0
            )
            self.item_actions[self.inventory.active_item]()

    def pickup(self, item: Item):
        if item in self.inventory.inventory:
            self.inventory.inventory[item] += 1
        else:
            self.inventory.inventory[item] = 1

    def _trigger_whack_animation(self):
        if self._whack_animation_start:
            return
        self._whack_animation_start = time.monotonic()
