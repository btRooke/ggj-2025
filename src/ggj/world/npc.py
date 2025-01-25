from dataclasses import dataclass

from .item import Item


@dataclass
class NPC:

    name: str
    states: dict[str, str]
    inventory: dict[Item, int]
