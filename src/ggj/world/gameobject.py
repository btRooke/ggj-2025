from typing import Protocol, TypeVar
from math import sqrt

SelfGameObject = TypeVar("SelfGameObject", bound="GameObject")

class GameObject(Protocol):
    def update(self) -> None: ...
    def draw(self) -> None: ...
    def get_pos(self) -> tuple[int, int]: ...
    """
    The 'z-index' is the priority in which the object is
    drawn when multiple objects are on the same tile.

    The lower the z-index the higher priority
    """
    def zindex(self) -> int: ...
    """
    Returns True if chracters cannot move through the object
    """
    def impassable(self) -> bool: ...

class Collidable():
    """
    When two objects are on the same tile they are said to be
    colliding. This callback gets fired when they both
    collide.
    """
    def on_collide(self, object: GameObject): ...

class Wiedable():
    """
    Objects that implement this can be picked up and perform an 'action'.
    Examples of wiedable items may be a scythe or a shovel.
    """
    def execute(self): ...


class GameObjectUtils:
    @staticmethod
    def distance(obj1: GameObject, obj2: GameObject) -> float:
        obj1_x, obj1_y = obj1.get_pos()
        obj2_x, obj2_y = obj2.get_pos()
        return sqrt((obj2_x - obj1_x) ** 2 + (obj2_y - obj1_y) ** 2) 
