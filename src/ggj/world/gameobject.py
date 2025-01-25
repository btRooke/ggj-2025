from typing import Protocol

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
