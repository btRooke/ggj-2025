import curses
import logging
import time
from typing_extensions import Any, Optional

from . import InterfaceObject
from ..world.player import PlayerInventory

logger = logging.getLogger(__name__)


class DialogueBox(InterfaceObject):

    def draw(self) -> None:
        self._w.border()
        self._ww.move(0, 0)
        self._w.refresh()

    HEIGHT = 10

    def __init__(self, root: curses.window, world_viewer_width: int):
        super().__init__()
        wh, ww = root.getmaxyx()
        self._w = root.subwin(
            self.HEIGHT,
            world_viewer_width + 2,
            round(wh * 0.818 - self.HEIGHT / 2),
            round(ww / 2 - (world_viewer_width + 2) / 2),
        )
        self._ww = self._w.derwin(
            self._w.getmaxyx()[0] - 2, self._w.getmaxyx()[1] - 4, 1, 2
        )

    def write(self, message: str):
        self._ww.clear()
        self._ww.move(0, 0)
        for i in range(len(message)):
            self._ww.addch(message[i])
            self._ww.refresh()
            time.sleep(0.015)


class OptionsMenu(InterfaceObject):

    WIDTH = 40
    HEIGHT = 35

    def __init__(self, parent: curses.window, i: int, j: int):
        super().__init__()
        self._w = parent.subwin(OptionsMenu.HEIGHT, OptionsMenu.WIDTH, i, j)
        self.options: dict[str, Any] = {}
        self._ww = self._w.derwin(
            OptionsMenu.HEIGHT - 4, OptionsMenu.WIDTH - 8, 2, 4
        )


class RightOptionsMenu(OptionsMenu):

    def __init__(self, root: curses.window, world_viewer_width: int):
        options_space_width = (root.getmaxyx()[1] - world_viewer_width) / 2
        super().__init__(
            root,
            round((root.getmaxyx()[0] - OptionsMenu.HEIGHT) / 2),
            round(
                options_space_width
                + world_viewer_width
                + options_space_width / 2
                - OptionsMenu.WIDTH / 2
            ),
        )
        self.options = {
            "TODO implement this": 0,
            "🌾 Plants planted": 42,
            "💸 Quids": 12,
            "🐛 Mutant Rats killed": 1,
        }
        self._required_redraw = True
        self._health_percentage = 0.72
        self._diag_options: list[str] = []

    def set_health(self, percentage: float) -> None:
        logger.info(f"health set to {percentage}")
        self._health_percentage = percentage
        self._required_redraw = True

    def set_diag_option(self, options: list[str]):
        self._diag_options = options
        self.draw()

    def draw(self) -> None:

        self._ww.move(0, 0)

        max = self._ww.getmaxyx()[1]
        lower = int(self._health_percentage * max)
        higher = max - lower
        self._ww.addstr("Health\n", curses.A_BOLD)
        self._ww.addstr("=" * lower, curses.color_pair(curses.COLOR_RED))
        self._ww.addstr("=" * higher, curses.color_pair(curses.COLOR_BLACK))
        self._ww.addstr("\n")

        # line

        self._ww.addstr(("─" * (self._ww.getmaxyx()[1]) + "\n"))

        # options

        for i, k in enumerate(self.options):

            if i != 0:
                self._ww.addstr("\n\n")

            self._ww.addstr(k, curses.A_BOLD)
            self._ww.addstr("\n")
            self._ww.addstr(str(self.options[k]))

        self._ww.addstr("\n\n")

        # line

        self._ww.addstr(("─" * (self._ww.getmaxyx()[1]) + "\n"))

        # diag

        if self._diag_options:

            self._ww.addstr("Dialogue Choices\n", curses.A_BOLD)

            for i, o in enumerate(self._diag_options, start=1):
                self._ww.addstr(f"{i}. {o}\n")

        self._w.border()
        self._w.refresh()
        self._ww.refresh()


class LeftOptionsMenu(OptionsMenu):

    def __init__(
        self,
        root: curses.window,
        world_viewer_width: int,
        inventory: PlayerInventory,
    ):
        options_space_width = (root.getmaxyx()[1] - world_viewer_width) / 2
        super().__init__(
            root,
            round((root.getmaxyx()[0] - OptionsMenu.HEIGHT) / 2),
            round(options_space_width / 2 - OptionsMenu.WIDTH / 2),
        )
        self.inventory = inventory
        self._required_redraw = True

    def draw(self) -> None:
        self._ww.clear()
        self._ww.move(0, 0)

        # equipped tool

        self._ww.addstr("🛠️  Equipped Tool\n", curses.A_BOLD)
        self._ww.addstr(
            self.inventory.active_item.name
            if self.inventory.active_item
            else "None"
        )
        self._ww.addstr("\n\n")

        if self.inventory.active_item:
            assert (
                "wieldable" in self.inventory.active_item.traits
                or "placeable" in self.inventory.active_item.traits
            )

        # line
        self._ww.addstr(("─" * (self._ww.getmaxyx()[1]) + "\n"))

        # inventory

        self._ww.addstr("Inventory\n", curses.A_BOLD)
        for n, i in enumerate(self.inventory.inventory, start=1):
            self._ww.addstr(f"{n}. {i.name} x {self.inventory.inventory[i]}\n")

        self._w.border()
        self._w.refresh()
        self._ww.refresh()


class WorldViewerBorder(InterfaceObject):

    def __init__(
        self, root_window: curses.window, world_viewer_window: curses.window
    ):
        super().__init__()
        world_viewer_height, world_viewer_width = world_viewer_window.getmaxyx()
        world_viewer_base_i, world_viewer_base_j = (
            world_viewer_window.getbegyx()
        )
        self._w = root_window.subwin(
            world_viewer_height + 3,
            world_viewer_width + 2,
            world_viewer_base_i - 1,
            world_viewer_base_j - 1,
        )
        self.direction_colours = {
            "n": curses.COLOR_WHITE,
            "e": curses.COLOR_WHITE,
            "s": curses.COLOR_WHITE,
            "w": curses.COLOR_RED,
        }
        self._flashers: dict[str, Optional[float]] = {
            "n": None,
            "e": None,
            "s": None,
            "w": None,
        }
        self._required_redraw = True

    def start_flashing(self, direction: str) -> None:
        if self._flashers[direction] is not None:
            return
        else:
            self._flashers[direction] = 0

    def stop_flashing(self, direction: str) -> None:
        if self._flashers[direction] is None:
            return
        else:
            self._flashers[direction] = None

    def update(self) -> None:

        current_time = time.monotonic()

        for direction in self._flashers:

            # if flasher active

            if (t := self._flashers[direction]) is not None:

                # if time passed switch colour

                if current_time - t > 0.35:

                    if self.direction_colours[direction] == curses.COLOR_RED:
                        self.direction_colours[direction] = curses.COLOR_WHITE
                    else:
                        self.direction_colours[direction] = curses.COLOR_RED

                    self._flashers[direction] = current_time
                    self._required_redraw = True

            # if not and still red, go to white

            elif self.direction_colours[direction] == curses.COLOR_RED:
                self.direction_colours[direction] = curses.COLOR_WHITE
                self._required_redraw = True

        super().update()

    def draw(self) -> None:
        uly, ulx = 0, 0
        lry, lrx = self._w.getmaxyx()
        lry -= 2
        lrx -= 1

        self._w.attron(curses.color_pair(self.direction_colours["w"]))
        self._w.vline(uly + 1, ulx, curses.ACS_VLINE, lry - uly - 1)
        self._w.attron(curses.color_pair(self.direction_colours["n"]))
        self._w.hline(uly, ulx + 1, curses.ACS_HLINE, lrx - ulx - 1)
        self._w.attron(curses.color_pair(self.direction_colours["s"]))
        self._w.hline(lry, ulx + 1, curses.ACS_HLINE, lrx - ulx - 1)
        self._w.attron(curses.color_pair(self.direction_colours["e"]))
        self._w.vline(uly + 1, lrx, curses.ACS_VLINE, lry - uly - 1)
        self._w.attron(curses.color_pair(curses.COLOR_WHITE))
        self._w.addch(uly, ulx, curses.ACS_ULCORNER)
        self._w.addch(uly, lrx, curses.ACS_URCORNER)
        self._w.addch(lry, lrx, curses.ACS_LRCORNER)
        self._w.addch(lry, ulx, curses.ACS_LLCORNER)

        self._w.noutrefresh()
