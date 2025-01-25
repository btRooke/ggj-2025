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


LOG_NAME = Path(f"logs/{datetime.datetime.now()}.log")
LOG_NAME.parent.mkdir(exist_ok=True)
logging.basicConfig(
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    filename=LOG_NAME,
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)
PACKAGE_ROOT = Path(__file__).parent.resolve()


world_layout: list[list[int]] = [[0, 1, 1]]


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


def world_loop(stdscr: window):

    WorldManager.init(stdscr)

    def move():
        Camera.move_camera((-1, 0))
        stdscr.clear()

    il = KeyboardListener(stdscr)
    il.callbacks["a"] = move

    for y, row in enumerate(world_layout):
        for x, obj in enumerate(row):
            if obj == 1:
                r = ro.Rock(x * ro.ROCK_SIZE, y * ro.ROCK_SIZE, stdscr)
                WorldManager.add_object(r)

    stdscr.clear()
    stdscr.refresh()

    while True:
        WorldManager.draw()
        il.check_input()


if __name__ == "__main__":
    _run_mypy()
    try:
        curses.wrapper(world_loop)
    except (KeyboardInterrupt, Exception) as e:
        logger.debug("stopping game")
        raise
