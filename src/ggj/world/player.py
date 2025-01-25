from curses import window
from ..drawing import shape as s
from .camera import Camera

MOVE_CAMERA_COLS = 5

class Player:
    def __init__(self, x: int, y: int, win: window):
        self.window = win
        self.pos: list[int] = [x, y]

    def update(self):
        pass

    def draw(self):
        x, y = self.pos
        s.world_char(self.window, x, y, '#', s.DARK_RED)

    def get_pos(self) -> tuple[int, int]:
        return self.pos[0], self.pos[1]

    def zindex(self) -> int:
        return -10

    def move(self, move_vector: tuple[int, int]):
        x, y = move_vector
        self.pos[0] += x
        self.pos[1] += y

        player_x, player_y = self.get_pos()
        cam_x, cam_y = Camera.get_pos()

        x_exceeded = abs(cam_x - player_x) >= MOVE_CAMERA_COLS
        y_exceeded = abs(cam_y - player_y) >= MOVE_CAMERA_COLS

        # determine if player exceeds bounding box. Move camra if player
        # out of bounding box
        if x_exceeded or y_exceeded:
            Camera.move_camera(move_vector)
