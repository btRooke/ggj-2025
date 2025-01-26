from typing import ClassVar, Optional, Dict
from curses import window
from .gameobject import GameObject, Collidable
from .camera import Camera
import logging

logger = logging.getLogger(__name__)


class WorldManager:
    objects: ClassVar[list[GameObject]] = []
    screen: ClassVar[Optional[window]] = None

    @staticmethod
    def add_object(obj: GameObject):
        WorldManager.objects.append(obj)
        logger.debug(f"added {obj} to world")

    @staticmethod
    def update():
        Camera.update()

        for obj in WorldManager.objects:
            obj.update()

    @staticmethod
    def get_collisions() -> dict[tuple[int, int], list[GameObject]]:

        collidables = [
            o for o in WorldManager.objects if isinstance(o, Collidable)
        ]
        locations = set(o.get_pos() for o in collidables)
        locations_to_objects = {
            l: [o for o in collidables if o.get_pos() == l] for l in locations
        }
        collisions = {
            k: v for k, v in locations_to_objects.items() if len(v) > 1
        }

        if collisions:
            logger.info(f"collisions {collisions}")

        return collisions

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
            coord_dict[(x, y)] = objs

        for objs in coord_dict.values():
            for obj in objs:
                obj.draw()

    @staticmethod
    def init(screen: window):
        WorldManager.screen = screen

    @staticmethod
    def _get_impassable_objects(x: int, y: int) -> list[GameObject]:
        return list(
            filter(
                lambda o: o.get_pos() == (x, y) and not o.impassable(),
                WorldManager.objects,
            )
        )

    @staticmethod
    def get_objects(x: int, y: int) -> list[GameObject]:
        return list(
            filter(lambda o: o.get_pos() == (x, y), WorldManager.objects)
        )

    """
    Determine if the given square is 'placeable'. Meaning that
    an object can be put on the square or the player can move
    to the square.
    """

    @staticmethod
    def can_place(x: int, y: int) -> int:
        return len(WorldManager._get_impassable_objects(x, y)) > 0

    @staticmethod
    def clear_cell(x: int, y: int):
        """
        clear all objects in the given location that is not the player
        """
        assert WorldManager.screen
        objs = WorldManager._get_impassable_objects(x, y)
        # all terrain is at zindex 0
        objs = list(filter(lambda o: o.zindex() == 0, objs))

        for obj in objs:
            logging.debug(f"Removed object {len(objs)}")
            WorldManager.objects.remove(obj)
