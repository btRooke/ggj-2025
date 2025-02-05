import logging
import time
from dataclasses import dataclass

from typing_extensions import Callable

logger = logging.getLogger(__name__)


@dataclass
class Event:
    time: float
    action: Callable[[], None]
    done: bool = False


class Events:
    def __init__(self, events: list[Event]):
        self._start = time.monotonic()
        self._events = sorted(events, key=lambda e: e.time)

    def check(self):
        for e in self._events:
            if e.done:
                continue
            if time.monotonic() - self._start < e.time:
                break
            e.done = True
            logger.info(f"triggering event {e.action}")
            e.action()

    def done(self) -> bool:
        return all((e.done for e in self._events))
