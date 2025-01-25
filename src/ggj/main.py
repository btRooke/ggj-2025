import curses
import datetime
import logging
import sys
from curses import window
from pathlib import Path
from typing import Optional

from mypy import api

from .input import KeyboardListener

logging.basicConfig(
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    filename=f"{datetime.datetime.now()}.log",
    level=logging.DEBUG,
)
il: Optional[KeyboardListener] = None  # TODO sort this out...
logger = logging.getLogger(__name__)
PACKAGE_ROOT = Path(__file__).parent.resolve()


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


def example_draw_rectangle(stdscr: window):
    global il

    stdscr.clear()

    coords = Coords(3, 3)

    il = KeyboardListener(stdscr)
    il.callbacks["w"] = lambda: coords.s()
    il.callbacks["s"] = lambda: coords.n()
    il.callbacks["a"] = lambda: coords.w()
    il.callbacks["d"] = lambda: coords.e()
    il.start()

    while True:
        stdscr.refresh()
        stdscr.addch(coords.y, coords.x, "#")


if __name__ == "__main__":
    _run_mypy()
    try:
        curses.wrapper(example_draw_rectangle)
    except (KeyboardInterrupt, Exception) as e:
        logger.debug("stopping whole program")
        if il is not None:
            logger.debug("stopping input listener")
            il.shutdown()
        curses.endwin()
        raise
