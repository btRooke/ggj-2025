import curses
import datetime
import logging
import sys
from curses import window
from pathlib import Path
from typing import Optional

from mypy import api

from .input import KeyboardListener
from .world import rock as ro
from .world.camera import Camera
from .world.manager import WorldManager

logging.basicConfig(
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    filename=f"{datetime.datetime.now()}.log",
    level=logging.DEBUG,
)
il: Optional[KeyboardListener] = None  # TODO sort this out...
logger = logging.getLogger(__name__)
PACKAGE_ROOT = Path(__file__).parent.resolve()


world_layout: list[list[int]] = [
    [0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
]


def _run_mypy() -> None:
    """
    Run Tim's mypy checker on the package before the game starts.

    Program exits if error code is bad.
    """
    out, err, code = api.run([str(PACKAGE_ROOT)])
    print(out, file=sys.stdout, end="")
    print(err, file=sys.stderr, end="")
    if code != 0:
        exit(code)


class Coords:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def n(self):
        self.y += 1

    def e(self):
        self.x += 1

    def s(self):
        self.y -= 1

    def w(self):
        self.x -= 1


def world_loop(stdscr: window):
    # global il
    #
    # coords = Coords(3, 3)
    # il = KeyboardListener(stdscr)
    # il.callbacks["w"] = lambda: coords.s()
    # il.callbacks["s"] = lambda: coords.n()
    # il.callbacks["a"] = lambda: coords.w()
    # il.callbacks["d"] = lambda: coords.e()
    # il.start()

    c = Camera()
    WorldManager.init(stdscr, c)

    for y, row in enumerate(world_layout):
        for x, obj in enumerate(row):
            if obj == 1:
                r = ro.Rock(x * ro.ROCK_SIZE, y * ro.ROCK_SIZE, stdscr)
                WorldManager.add_object(r)

    stdscr.clear()
    stdscr.refresh()

    while True:
        WorldManager.draw()


if __name__ == "__main__":
    _run_mypy()
    try:
        curses.wrapper(world_loop)
    except Exception as e:
        logger.debug("stopping game")
        curses.endwin()
        if il:
            logger.debug("stopping IL")
            il.shutdown()
        raise
