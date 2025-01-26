import curses
import logging
import sys
import time
from curses import window
from pathlib import Path

from mypy import api

from ggj.interface.conversation import Conversations
from ggj.world.item import WHEAT, QUID
from ggj.world.npc import Farmer, NPC
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
    level=logging.DEBUG,
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

    stats = {"plants": 0, "rats": 0, "quids": 0, "bubb": 0}

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

    def rat_cb(n: int):
        stats["rats"] += n
        update_inv_ui()

    def wheat_cb(n: int):
        stats["plants"] += n
        update_inv_ui()

    # hook up movement
    p = player.Player(player_start_x, player_start_y)
    p.inventory.inventory[WHEAT] = 2
    p.rat_cb = rat_cb
    p.wheat_harvested_cb = wheat_cb
    WorldManager.add_object(p)

    # interface components
    diag_box = DialogueBox(stdscr, world_window.getmaxyx()[1])
    inv_box = LeftOptionsMenu(stdscr, world_window.getmaxyx()[1], p.inventory)
    right_box = RightOptionsMenu(stdscr, world_window.getmaxyx()[1], stats)
    right_box.set_health(0.43)  # TODO hook up health
    world_viewer_border = WorldViewerBorder(stdscr, world_window)
    interface_components: list[InterfaceObject] = [
        world_viewer_border,
        right_box,
        inv_box,
        diag_box,
    ]

    def update_inv_ui():
        inv_box._required_redraw = True
        right_box._required_redraw = True

    p.inventory.update_inv_cb = update_inv_ui

    rat_overseer = rat.RatOverseer()
    WorldManager.add_object(rat_overseer)

    def set_rat_indicators(rat_dirs: set[str]):
        dirs = {"n", "e", "s", "w"}

        for d in rat_dirs:
            world_viewer_border.start_flashing(d)

        for d in dirs - rat_dirs:
            world_viewer_border.stop_flashing(d)

    rat_overseer.set_on_all_rats(lambda: set_rat_indicators(set()))
    rat_overseer.set_on_rat_hidden(lambda dirs: set_rat_indicators(dirs))

    WorldManager.add_object(Farmer())

    il = KeyboardListener(stdscr)

    conversations = Conversations(p, inv_box, diag_box, right_box, il)

    def move(move_vector: tuple[int, int]):
        p.move(move_vector)

    def swap_item():
        p.inventory.next_active()
        inv_box._required_redraw = True

    def place_rat():
        p_x, p_y = p.get_pos()
        r = rat.Rat(p_x, p_y)
        WorldManager.add_object(r)

    def talk_to_npc():
        npc = list(
            filter(
                lambda o: isinstance(o, NPC)
                and o.get_pos() in p.get_surrounding(),
                WorldManager.objects,
            )
        )
        if len(npc) < 1:
            return
        conversations.converse(npc[0])

        if QUID in p.inventory.inventory:
            stats["quids"] = p.inventory.inventory[QUID]
            update_inv_ui()

    il.callbacks["a"] = lambda: move((-1, 0))
    il.callbacks["d"] = lambda: move((1, 0))
    il.callbacks["s"] = lambda: move((0, 1))
    il.callbacks["w"] = lambda: move((0, -1))
    il.callbacks["x"] = lambda: p.execute()
    il.callbacks["e"] = swap_item
    il.callbacks["r"] = place_rat
    il.callbacks["t"] = talk_to_npc

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
