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
    filename="ggj.log",
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

    # calculate where to put world viewer

    max_height, max_width = stdscr.getmaxyx()
    world_height, world_width = max_height * 0.75, max_width * 0.75
    world_window = curses.newwin(
        int(world_height),
        int(world_width),
        int(max_height / 2 - world_height / 2),
        int(max_width / 2 - world_width / 2),
    )
    WorldManager.init(world_window)
    assert WorldManager.screen is not None
    logger.info(f"whole screen beginning y/x {stdscr.getbegyx()}")
    logger.info(f"whole screen dims y/x {stdscr.getmaxyx()}")
    logger.info(f"world beginning y/x {WorldManager.screen.getbegyx()}")
    logger.info(f"whole screen y/x {WorldManager.screen.getmaxyx()}")

    # hook up movement

    def move():
        Camera.move_camera((-1, 0))
        stdscr.clear()

    il = KeyboardListener(stdscr)
    il.callbacks["a"] = move

    # put some rocks in the world

    for y, row in enumerate(world_layout):
        for x, obj in enumerate(row):
            if obj == 1:
                r = ro.Rock(x * ro.ROCK_SIZE, y * ro.ROCK_SIZE, world_window)
                WorldManager.add_object(r)

    stdscr.clear()
    stdscr.refresh()

    # main loop

    while True:
        WorldManager.draw()
        il.check_input()


if __name__ == "__main__":
    _run_mypy()
    logger.info(f"new game started")
    try:
        curses.wrapper(world_loop)
    except (KeyboardInterrupt, Exception) as e:
        logger.debug("stopping game")
        raise
