import curses
import logging
import sys
import time
from curses import window
from pathlib import Path

from mypy import api

from ggj.world.npc import Farmer
from .events import Events
from .input import KeyboardListener
from .interface import InterfaceObject
from .interface.windows import (
    WorldViewerBorder,
    RightOptionsMenu,
    LeftOptionsMenu,
    DialogueBox,
)
from .world import player
from .world import rat
from .world import terrain
from .world.camera import Camera
from .world.manager import WorldManager
from .world.tiles import WORLD_TILES

logging.basicConfig(
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    filename="ggj.log",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
PACKAGE_ROOT = Path(__file__).parent.resolve()

GAME_TICK_FREQUENCY = 30
EVENT_TICK_FREQUENCY = 10


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

    # curses stuff

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
        int(max_height * 0.36 - world_height / 2),
        int(max_width * 0.5 - world_width / 2),
    )
    WorldManager.init(world_window)
    assert WorldManager.screen is not None
    logger.info(f"whole screen beginning y/x {stdscr.getbegyx()}")
    logger.info(f"whole screen dims y/x {stdscr.getmaxyx()}")
    logger.info(f"world beginning y/x {WorldManager.screen.getbegyx()}")
    logger.info(f"world screen y/x {WorldManager.screen.getmaxyx()}")

    terrain.TerrainFactory.create_terrain(WORLD_TILES)

    player_start_x = int(len(WORLD_TILES[0]) / 2)
    player_start_y = int(len(WORLD_TILES[1]) / 2)

    Camera.move_camera((player_start_x, player_start_y))

    # hook up movement
    p = player.Player(player_start_x, player_start_y)
    WorldManager.add_object(p)

    # interface components

    diag_box = DialogueBox(stdscr, world_window.getmaxyx()[1])
    inv_box = LeftOptionsMenu(stdscr, world_window.getmaxyx()[1], p.inventory)
    right_box = RightOptionsMenu(stdscr, world_window.getmaxyx()[1])
    right_box.set_health(0.43)  # TODO hook up health
    world_viewer_border = WorldViewerBorder(stdscr, world_window)
    interface_components: list[InterfaceObject] = [
        world_viewer_border,
        right_box,
        inv_box,
        diag_box,
    ]

    world_viewer_border.start_flashing("n")

    WorldManager.add_object(Farmer(diag_box))

    def move(move_vector: tuple[int, int]):
        p.move(move_vector)

    def swap_item():
        p.inventory.next_active()
        inv_box._required_redraw = True

    def place_rat():
        p_x, p_y = p.get_pos()
        r = rat.Rat(p_x, p_y)
        WorldManager.add_object(r)

    il = KeyboardListener(stdscr)
    il.callbacks["a"] = lambda: move((-1, 0))
    il.callbacks["d"] = lambda: move((1, 0))
    il.callbacks["s"] = lambda: move((0, 1))
    il.callbacks["w"] = lambda: move((0, -1))
    il.callbacks["x"] = lambda: p.execute()
    il.callbacks["e"] = swap_item
    il.callbacks["r"] = place_rat

    # put rocks in
    world_window.nodelay(True)

    stdscr.clear()
    stdscr.refresh()

    world_window.clear()
    world_window.refresh()

    # events
    events = Events([])

    # main loop
    last_tick = 0.0
    last_game_tick = 0.0

    while True:
        WorldManager.draw()
        current_time = time.monotonic()

        if (time.monotonic() - last_game_tick) > (1 / GAME_TICK_FREQUENCY):
            WorldManager.update()
            for c in interface_components:
                c.update()

        if (time.monotonic() - last_tick) < (1 / EVENT_TICK_FREQUENCY):
            continue

        last_tick = current_time

        il.check_input()
        events.check()


if __name__ == "__main__":
    _run_mypy()
    logger.info(f"new game started")
    try:
        curses.wrapper(world_loop)
    except (KeyboardInterrupt, Exception) as e:
        logger.debug("stopping game")
        raise
