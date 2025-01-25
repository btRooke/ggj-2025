import curses
import logging
from dataclasses import dataclass, field
from typing import Optional

from .camera import Camera
from .gameobject import Collidable, GameObject
from .item import Item, SHOVEL, WOODEN_STICK
from .manager import WorldManager
from .terrain import Hole
from ..drawing import shape as s

MOVE_CAMERA_COLS = 5
logger = logging.getLogger(__name__)


@dataclass
class PlayerInventory:
    inventory: dict[Item, int] = field(default_factory=dict)
    active_item: Optional[Item] = None

    def next_active(self) -> None:
        items: list[Item] = sorted(self.inventory, key=lambda x: x.name)
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


class Player(Collidable):
    def __init__(self, x: int, y: int):
        self.pos: list[int] = [x, y]

        # inventory

        self.inventory = PlayerInventory()
        self.inventory.inventory[SHOVEL] = 1
        self.inventory.inventory[WOODEN_STICK] = 1
        self.inventory.active_item = SHOVEL

        # item actions

        self.item_actions = {SHOVEL: self.dig}

    def update(self):
        pass

    def dig(self):
        x, y = self.get_pos()
        WorldManager.clear_cell(x, y)
        WorldManager.add_object(Hole(x, y))

    def draw(self):
        assert WorldManager.screen
        x, y = self.pos
        s.world_char(WorldManager.screen, x, y, "#", s.DARK_RED)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

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
        return False

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
