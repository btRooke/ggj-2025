import curses
import logging
from curses import textpad

from . import InterfaceObject

logger = logging.getLogger(__name__)


class OptionsMenu(InterfaceObject):

    WIDTH = 40
    HEIGHT = 35

    def __init__(self, parent: curses.window, i: int, j: int):
        super().__init__()
        self._w = parent.subwin(OptionsMenu.HEIGHT, OptionsMenu.WIDTH, i, j)
        self._ww = self._w.derwin(
            OptionsMenu.HEIGHT - 4, OptionsMenu.WIDTH - 8, 2, 4
        )
        self.options = {
            "🌾 Plants planted": 42,
            "💸 Quids": 12,
            "🐀 Rats killed": 1,
        }

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
