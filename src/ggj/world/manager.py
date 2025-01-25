from typing import ClassVar, Optional
from curses import window, textpad
from .gameobject import GameObject
from .camera import Camera


class WorldManager:
    objects: ClassVar[list[GameObject]] = []
    screen: ClassVar[Optional[window]] = None

    @staticmethod
    def add_object(obj: GameObject):
        WorldManager.objects.append(obj)

    @staticmethod
    def update():
        Camera.update()

        for obj in WorldManager.objects:
            obj.update()

    @staticmethod
    def draw():
        if not WorldManager.screen:
            raise Exception("not initialised the screen")

        WorldManager.screen.refresh()

        max = WorldManager.screen.getmaxyx()

        textpad.rectangle(
            WorldManager.screen,
            1,
            1,
            max[0] - 2,
            max[1] - 2,
        )

        for obj in WorldManager.objects:
            obj.draw()

    @staticmethod
    def init(screen: window):
        WorldManager.screen = screen
