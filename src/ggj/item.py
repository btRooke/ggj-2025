from dataclasses import dataclass


@dataclass()
class Item:
    name: str
    traits: list[str]

    def __hash__(self):
        return hash(str)
