import curses
import logging
import sys
from curses import window
from pathlib import Path
from mypy import api
from .input import KeyboardListener
from .world import terrain
from .world import player
from .world.camera import Camera
from .interface import InterfaceObject
from .interface.windows import WorldViewerBorder, RightOptionsMenu
from .world.manager import WorldManager

logging.basicConfig(
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    filename="ggj.log",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)
PACKAGE_ROOT = Path(__file__).parent.resolve()


world_layout: list[list[int]] = [
    [i in {0, 49} or x in {0, 49} for i in range(0, 50)] for x in range(0, 50)
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


LIM_X: int = 150
LIM_Y: int = 100


def generate_world(screen: window):
    offset = 10

    for y in range(LIM_Y):
        for x in range(LIM_X):
            if offset <= x < LIM_X - offset and offset <= y < LIM_Y - offset:
                WorldManager.add_object(terrain.Grass(x, y, screen))

            else:
                WorldManager.add_object(terrain.Boundary(x, y, screen))


def world_loop(stdscr: window):
    curses.use_default_colors()
    curses.start_color()
    curses.curs_set(False)

    for i in range(curses.COLORS):
        curses.init_pair(i, i, -1)

    # calculate where to put world viewer
    max_height, max_width = stdscr.getmaxyx()
    world_height, world_width = 20, 20 * 2
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
    logger.info(f"world screen y/x {WorldManager.screen.getmaxyx()}")

    player_start_x = int(LIM_X / 2)
    player_start_y = int(LIM_Y / 2)

    # interface components

    interface_components: list[InterfaceObject] = [
        WorldViewerBorder(stdscr, world_window),
        RightOptionsMenu(stdscr, world_window.getmaxyx()[1]),
        # LeftOptions(stdscr),
        # RightOptions(stdscr)
    ]

    Camera.move_camera((player_start_x, player_start_y))
    # hook up movement
    p = player.Player(player_start_x, player_start_y, world_window)
    WorldManager.add_object(p)

    def move(move_vector: tuple[int, int]):
        p.move(move_vector)
        world_window.erase()

    il = KeyboardListener(stdscr)
    il.callbacks["a"] = lambda: move((-1, 0))
    il.callbacks["d"] = lambda: move((1, 0))
    il.callbacks["s"] = lambda: move((0, 1))
    il.callbacks["w"] = lambda: move((0, -1))

    # put rocks in
    world_window.nodelay(True)

    generate_world(world_window)

    stdscr.clear()
    stdscr.refresh()

    world_window.clear()
    world_window.refresh()

    # main loop
    while True:
        WorldManager.draw()
        for c in interface_components:
            c.update()
        il.check_input()

if __name__ == "__main__":
    _run_mypy()
    logger.info(f"new game started")
    try:
        curses.wrapper(world_loop)
    except (KeyboardInterrupt, Exception) as e:
        logger.debug("stopping game")
        raise
