import curses
import logging
import time
from curses import textpad
from typing import Any

from . import InterfaceObject
from ..world.item import Item
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
            time.sleep(0.028)


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

    def draw(self) -> None:

        self._ww.move(0, 0)

        for i, k in enumerate(self.options):

            if i != 0:
                self._ww.addstr("\n\n")

            self._ww.addstr(k, curses.A_BOLD)
            self._ww.addstr("\n")
            self._ww.addstr(str(self.options[k]))

        self._w.border()
        self._w.refresh()
        self._ww.refresh()


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
            "🌾 Plants planted": 42,
            "💸 Quids": 12,
            "🐛 Mutant Rats killed": 1,
        }
        self._required_redraw = True


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
            assert "wieldable" in self.inventory.active_item.traits

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
            world_viewer_width + 3,
            world_viewer_base_i - 1,
            world_viewer_base_j - 1,
        )
        self._required_redraw = True

    def draw(self) -> None:
        h, w = self._w.getmaxyx()
        textpad.rectangle(self._w, 0, 0, h - 2, w - 2)  # TODO hack for now
        self._w.refresh()
