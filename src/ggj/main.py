import sys
from pathlib import Path
from mypy import api
import curses
from curses import window
from .drawing import shape as s
from .world import rock as ro
from .world.manager import WorldManager
from .world.camera import Camera

PACKAGE_ROOT = Path(__file__).parent.resolve()

world_layout: list[list[int]] = [
    [0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 0 ,0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 0 ,0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 0 ,0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 0 ,0],
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

def world_loop(stdscr: window):
    c = Camera()
    WorldManager.init(stdscr, c)

    for y, row in enumerate(world_layout):
        for x, obj in enumerate(row):
            if obj == 1:
                r = ro.Rock (x * ro.ROCK_SIZE, y * ro.ROCK_SIZE, stdscr)
                WorldManager.add_object(r)

    stdscr.clear()
    stdscr.refresh()

    while True:
        WorldManager.draw()

if __name__ == "__main__":
    _run_mypy()
    try:
        curses.wrapper (world_loop)
    except Exception as e:
        curses.endwin()
        raise
