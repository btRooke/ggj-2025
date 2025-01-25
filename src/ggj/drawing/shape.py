import curses.textpad as text
from curses import window
from ..world.camera import Camera

def rect(win: window, start_x: int, start_y: int, end_x: int,\
        end_y: int) -> None:
    text.rectangle (win, start_x, start_y, end_x, end_y)

def world_rect(win: window, start_x: int, start_y: int, end_x: int,\
                    end_y: int):
    cam_x, cam_y = Camera.get_pos()

    screen_start_x = max(0, start_x - cam_x)
    screen_start_y = max(0, start_y - cam_y)
    screen_end_x = max(0, end_x - cam_x)
    screen_end_y = max(0, end_y - cam_y)

    rect(win, screen_start_x, screen_start_y, screen_end_x, screen_end_y)
