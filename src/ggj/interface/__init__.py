from abc import ABC, abstractmethod


class InterfaceObject(ABC):

    def __init__(self):
        self._required_redraw = True

    @abstractmethod
    def draw(self) -> None: ...

    def update(self) -> None:
        if self._required_redraw:
            self.draw()
            self._required_redraw = False
