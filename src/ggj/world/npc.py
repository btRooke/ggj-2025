import curses
from abc import ABC, abstractmethod

from .gameobject import GameObject, Collidable
from .manager import WorldManager
from ..drawing import shape as s
from ..interface.windows import DialogueBox


class NPC(ABC, GameObject, Collidable):

    def __init__(
        self,
        name: str,
        icon: str,
        states: dict[str, str],
        current_state: str,
        location: tuple[int, int],
    ):
        self.name = name
        assert len(icon) == 1
        self.icon = icon
        assert current_state in states
        self.states = states
        self.current_state = current_state
        self.location = location

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

    @abstractmethod
    def on_collide(self, object: GameObject): ...


class Farmer(NPC):

    def on_collide(self, object: GameObject):
        self._diag_box.write(self.states[self.current_state])

    def __init__(self, diag_box: DialogueBox):
        super().__init__(
            "The Farmer",
            "%",
            {"start": "Hope you're ready to kill some PESTERLY EVIL rats!"},
            "start",
            (25, 25),
        )
        self._diag_box = diag_box
