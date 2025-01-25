import curses
import datetime
import logging
import sys
from curses import window
from pathlib import Path
from mypy import api
from .input import KeyboardListener
from .world import terrain
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


world_layout: list[list[int]] = [[i in {0, 49} or x in {0, 49} for i in range (0, 50)] for x in range(0, 50)]

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

def generate_world(screen: window):
    lim_x = 125
    lim_y = 40

    offset = 2

    for y in range(lim_y):
        for x in range(lim_x):
            if offset <= x < lim_x - offset and offset <= y < lim_y - offset:
                WorldManager.add_object(terrain.Rock(x, y, screen))
            else:
                WorldManager.add_object(terrain.Boundary(x, y, screen))

def world_loop(stdscr: window):
    curses.use_default_colors()
    curses.start_color()
    curses.curs_set(False)

    for i in range(curses.COLORS):
        curses.init_pair(i, i, -1)

    WorldManager.init(stdscr)

    def move(move_vector: tuple[int, int]):
        Camera.move_camera(move_vector)
        stdscr.clear()

    il = KeyboardListener(stdscr)
    il.callbacks["a"] = lambda: move((1, 0))
    il.callbacks["d"] = lambda: move((-1, 0))
    il.callbacks["s"] = lambda: move((0, -1))
    il.callbacks["w"] = lambda: move((0, 1))

    generate_world(stdscr)

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
