from typing import ClassVar, Optional, Dict
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

        coord_dict: Dict[tuple[int, int], list[GameObject]] = dict()

        for obj in WorldManager.objects:
            x, y = obj.get_pos()
            objs = coord_dict.get((x, y), [])
            objs.append(obj)
            objs.sort(key=lambda o: -o.zindex())
            coord_dict[(x,y)] = objs

        for objs in coord_dict.values():
            for obj in objs:
                obj.draw()


    @staticmethod
    def init(screen: window):
        WorldManager.screen = screen
