from dataclasses import dataclass, field


@dataclass()
class Item:
    name: str
    traits: list[str] = field(default_factory=list)

    def __hash__(self):
        return hash(str)


SHOVEL = Item("Shovel", ["wieldable"])
WOODEN_STICK = Item("Wooden Stick", ["wieldable", "weapon"])
SEEDS = Item("Seed", ["placeable", "wieldable"])
SCYTHE = Item("Scythe", ["wieldable"])
WHEAT = Item("Wheat")
QUID = Item("Quid")
