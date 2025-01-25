import curses
import logging

logger = logging.getLogger(__name__)


class KeyboardListener:

    def __init__(self, w: curses.window):
        super().__init__()
        self.callbacks: dict = {}
        self._w = w
        self._running = True
        self._w.nodelay(True)  # ms

    def check_input(self):

        raw_char = self._w.getch()
        if raw_char == curses.ERR:
            return
        c = chr(raw_char)
        logger.debug(f"got char {c}")
        if c in self.callbacks:
            self.callbacks[c]()
        while self._w.getch() != curses.ERR:
            pass
