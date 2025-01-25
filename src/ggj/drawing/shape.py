import curses.textpad as text
from curses import window

def rect(win: window, start_x: int, start_y: int, end_x: int,\
        end_y: int) -> None:
    text.rectangle (win, start_x, start_y, end_x, end_y)
