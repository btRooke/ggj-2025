from typing import ClassVar, Optional
from curses import window
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
            raise Exception ("not initialised the screen")

        WorldManager.screen.refresh()

        for obj in WorldManager.objects:
            obj.draw()

    @staticmethod
    def init(screen: window):
        WorldManager.screen = screen
