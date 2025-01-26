import curses
from abc import ABC, abstractmethod

from .gameobject import GameObject, Collidable
from .manager import WorldManager
from ..drawing import shape as s
from ..interface.windows import DialogueBox


class NPC(ABC, GameObject):

    def __init__(
        self,
        name: str,
        icon: str,
        states: dict[str, str],
        current_state: str,
        location: tuple[int, int],
        trade_as_buyer: str = "Let's see what you've got...",
        trade_as_seller: str = "Have a proper good peruse of my wares...",
        trade_success: str = "Thanks for doing business with me.",
        trade_fail: str = "Not a good deal, sorry.",
    ):
        self.name = name
        assert len(icon) == 1
        self.icon = icon
        assert current_state in states
        self.states = states
        self.current_state = current_state
        self.location = location

        # trade comments

        self.trade_as_buyer = trade_as_buyer
        self.trade_as_seller = trade_as_seller
        self.trade_success = trade_success
        self.trade_fail = trade_fail

    def update(self) -> None:
        pass

    def draw(self) -> None:
        assert WorldManager.screen
        x, y = self.location
        s.world_char(
            WorldManager.screen, x, y, self.icon, colour=curses.COLOR_RED
        )

    def get_pos(self) -> tuple[int, int]:
        return self.location

    def zindex(self) -> int:
        return -1

    def impassable(self) -> bool:
        return False


class Farmer(NPC):

    def __init__(self):
        super().__init__(
            "The Farmer",
            "%",
            {"start": "Hope you're ready to kill some PESTERLY EVIL rats!"},
            "start",
            (25, 25),
        )
