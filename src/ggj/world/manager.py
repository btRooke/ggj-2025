from typing import ClassVar, Optional, Dict
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

    @staticmethod
    def _get_objects(x: int, y:int) -> list[GameObject]:
        return list(filter(lambda o: o.get_pos() == (x, y) and not o.impassable(),
                           WorldManager.objects))

    """
    Determine if the given square is 'placeable'. Meaning that
    an object can be put on the square or the player can move
    to the square.
    """
    @staticmethod
    def can_place(x: int, y: int) -> int:
        return len(WorldManager._get_objects(x, y)) > 0

    @staticmethod
    def clear_cell(x: int, y: int):
        """
        clear all objects in the given location that is not the player
        """
        objs = WorldManager._get_objects(x, y)
        # all terrain is at zindex 0
        objs = list(filter(lambda o: o.zindex() == 0, objs))

        for obj in objs:
            WorldManager.objects.remove(obj)
