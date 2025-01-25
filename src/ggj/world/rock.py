from curses import window
from ..drawing import shape as s

ROCK_SIZE = 5


class Rock:
    def __init__(self, x: int, y: int, win: window):
        self.window = win
        self.pos = [x, y]

    def update(self):
        pass

    def draw(self):
        x, y = self.pos
        x += int(self.window.getbegyx()[1])
        y += int(self.window.getbegyx()[0])
        s.world_rect(
            self.window, x, y, x + (ROCK_SIZE - 1), y + (ROCK_SIZE - 1)
        )

    def get_pos(self):
        return tuple(self.pos)
