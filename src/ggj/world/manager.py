import logging
from curses import window
from typing import ClassVar, Optional, Set, Type

from ggj.drawing import shape as s
from ggj.world.gameobject import Collidable, GameObject

logger = logging.getLogger(__name__)


class WorldManager:
    objects: ClassVar[dict[tuple[int, int], list[GameObject]]] = dict()
    screen: ClassVar[Optional[window]] = None

    @staticmethod
    def add_object(obj: GameObject):
        objs = WorldManager.objects.get(obj.get_pos(), [])
        objs.append(obj)
        WorldManager.objects[obj.get_pos()] = objs

    @staticmethod
    def update():
        WorldManager._process_collisions()

        for _, objs in WorldManager.objects.items():
            for obj in objs:
                obj.update()

    @staticmethod
    def _group_by_position() -> dict[tuple[int, int], list[GameObject]]:
        return WorldManager.objects

    @staticmethod
    def _process_collisions():
        coord_dict = WorldManager._group_by_position()

        for pos_x, pos_y in coord_dict.keys():
            collidables = [
                o for o in coord_dict[(pos_x, pos_y)] if isinstance(o, Collidable)
            ]
            all_objects = coord_dict[(pos_x, pos_y)]

            if len(collidables) == 0:
                continue

            for i in range(len(collidables)):
                for j in range(len(all_objects)):
                    o1 = collidables[i]
                    o2 = all_objects[j]

                    if o1 == o2:
                        continue

                    o1.on_collide(o2)

    @staticmethod
    def draw():
        if not WorldManager.screen:
            raise Exception("not initialised the screen")

        WorldManager.screen.refresh()

        for x, y in WorldManager.objects.keys():
            objs = sorted(WorldManager.objects[(x, y)], key=lambda o: -o.zindex())
            for o in objs:
                o.draw()

    @staticmethod
    def init(screen: window):
        WorldManager.screen = screen

    @staticmethod
    def _get_impassable_objects(x: int, y: int) -> list[GameObject]:
        return list(
            filter(
                lambda o: o.impassable(),
                WorldManager.objects.get((x, y), []),
            )
        )

    @staticmethod
    def get_objects(x: int, y: int) -> list[GameObject]:
        objs = WorldManager.objects.get((x, y))
        assert objs
        logging.debug(objs)
        return objs

    """
    Determine if the given square is 'placeable'. Meaning that
    an object can be put on the square or the player can move
    to the square.
    """

    @staticmethod
    def can_place(x: int, y: int) -> int:
        return len(WorldManager._get_impassable_objects(x, y)) == 0

    @staticmethod
    def clear_cell(x: int, y: int):
        """
        clear all objects in the given location that is part
        of the terrain
        """
        assert WorldManager.screen
        objs = WorldManager.get_objects(x, y)
        objs = list(filter(lambda o: o.zindex() != 0, objs))
        WorldManager.objects[(x, y)] = objs

    @staticmethod
    def remove(obj: GameObject):
        logging.debug(f"Attempteng to remove f{obj}")
        objs = WorldManager.objects.get(obj.get_pos(), [])
        objs.remove(obj)

    @staticmethod
    def get_all_objects() -> list[GameObject]:
        os = []
        for objs in WorldManager.objects.values():
            for o in objs:
                os.append(o)

        return os

    @staticmethod
    def get_objects_of_type(types: Set[Type]) -> list[GameObject]:
        return list(filter(lambda o: type(o) in types, WorldManager.get_all_objects()))

    @staticmethod
    def get_visible_objects() -> list[GameObject]:
        assert WorldManager.screen
        return list(
            (
                o
                for o in WorldManager.get_all_objects()
                if s.in_bounds(WorldManager.screen, *o.get_pos())
            )
        )

    @staticmethod
    def get_out_of_sight_objects() -> list[GameObject]:
        assert WorldManager.screen
        return list(
            (
                o
                for o in WorldManager.get_all_objects()
                if not s.in_bounds(WorldManager.screen, *o.get_pos())
            )
        )
