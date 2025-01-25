import curses
from curses import window
from ..drawing import shape as s
from .camera import Camera
from .gameobject import Collidable, GameObject, Wiedable
from .manager import WorldManager

MOVE_CAMERA_COLS = 5

class Inventory:
    def __init__(self):
        self.inventory: list[Wiedable] = []
        self.active_idx = 0

    def set_active_idx(self, idx: int):
        self.active_idx = idx

    def length(self) -> int:
        return len(self.inventory)

    def get_items(self) -> list[Wiedable]:
        return list(self.inventory)

    def get_active(self) -> Wiedable:
        return self.inventory[self.active_idx]

    def add(self, wiedable: Wiedable):
        self.inventory.append(wiedable)

class Player(Collidable):
    def __init__(self, x: int, y: int):
        self.pos: list[int] = [x, y]
        self.inventory = Inventory()

    def update(self):
        pass

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
        return True

    def on_collide(self, object: GameObject):
        pass

    def execute(self):
        self.inventory.get_active().execute()

    def pickup(self, wiedable: Wiedable):
        self.inventory.add(wiedable)
