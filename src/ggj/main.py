import sys
from pathlib import Path
from mypy import api
import curses
from curses import window
from .drawing import shape as s

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

def example_draw_rectangle(stdscr: window):
    stdscr.clear()
    stdscr.refresh()

    while True:
        stdscr.refresh ()
        s.rect (stdscr, 1, 10, 20, 20)

if __name__ == "__main__":
    _run_mypy()
    try:
        curses.wrapper (example_draw_rectangle)
    except Exception as e:
        curses.endwin()
        raise
