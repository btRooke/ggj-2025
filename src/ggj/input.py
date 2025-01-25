import curses
import logging
from threading import Thread
from typing import override

logger = logging.getLogger(__name__)


class KeyboardListener(Thread):

    def __init__(self, w: curses.window):
        super().__init__()
        self.callbacks: dict = {}
        self._w = w
        self._running = True
        self._w.timeout(1000)  # ms

    @override
    def run(self):

        logger.debug(f"started listening")

        while self._running:
            raw_char = self._w.getch()
            logger.debug(f"got {raw_char}")
            if raw_char == curses.ERR:
                continue
            c = chr(raw_char)
            if c in self.callbacks:
                self.callbacks[c]()

        logger.debug(f"stopped listening")

    def shutdown(self):
        logger.debug(f"requested shutdown")
        self._running = False
