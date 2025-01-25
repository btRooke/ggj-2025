import curses
import curses.textpad as text
from curses import window
from ..world.camera import Camera

GREEN=108
DARK_GREEN=22

def rect(win: window, start_x: int, start_y: int, end_x: int,\
        end_y: int) -> None:
    text.rectangle (win, start_y, start_x, end_y, end_x)

def world_rect(win: window, start_x: int, start_y: int, end_x: int,\
                    end_y: int):
    cam_x, cam_y = Camera.get_pos()

    max_height, max_width = win.getmaxyx()

    screen_start_x = max(0, start_x - cam_x)
    screen_start_x = min(max_width, screen_start_x)

    screen_start_y = max(0, start_y - cam_y)
    screen_start_y = min(max_height, screen_start_y)

    screen_end_x = max(0, end_x - cam_x)
    screen_end_x = min(max_width, screen_end_x)

    screen_end_y = max(0, end_y - cam_y)
    screen_end_y = min(max_height, screen_end_y)

    rect(win, screen_start_x, screen_start_y, screen_end_x, screen_end_y)

def world_char(win: window, start_x: int, start_y: int, char: str, colour: int = 0):
    cam_x, cam_y = Camera.get_pos()
    cam_x += int(win.getbegyx()[1])
    cam_y += int(win.getbegyx()[0])

    max_height, max_width = win.getmaxyx()

    screen_x = (start_x - cam_x) * 2
    screen_y = start_y - cam_y


    if screen_x < 0 or screen_x >= max_width - 1:
        return

    if screen_y < 0 or screen_y >= max_height - 1:
        return


    win.addch(screen_y, screen_x, char, curses.color_pair(colour))
