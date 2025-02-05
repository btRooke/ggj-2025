import curses
import curses.textpad as text

from ggj.world.camera import Camera

GREEN = 108
DEEP_GREEN = 106
DARK_GREEN = 22
DARK_RED = 88
DEEP_BLUE = 21
GLISTEN_BLUE = 39
LIGHT_BROWN = 136
LIGHT_YELLOW = 184
GOLDEN = 178
MAROON = 52
BLOOD_RED = 52
HOT_PINK = 132
PURPLE = 129


def rect(
    win: curses.window, start_x: int, start_y: int, end_x: int, end_y: int
) -> None:
    text.rectangle(win, start_y, start_x, end_y, end_x)


def world_rect(win: curses.window, start_x: int, start_y: int, end_x: int, end_y: int):
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


def world_char(
    win: curses.window, start_x: int, start_y: int, char: str, colour: int = 0
):
    cam_x, cam_y = Camera.get_pos()

    max_height, max_width = win.getmaxyx()

    cam_x -= int(max_height / 2)
    cam_y -= int(max_height / 2)

    screen_x = (start_x - cam_x) * 2
    screen_y = start_y - cam_y

    if screen_x < 0 or screen_x > max_width - 1:
        return

    if screen_y < 0 or screen_y > max_height - 1:
        return

    win.addch(screen_y, screen_x, char, curses.color_pair(colour))


def in_bounds(win: curses.window, x: int, y: int) -> bool:
    cam_x, cam_y = Camera.get_pos()
    viewport, _ = win.getmaxyx()
    return abs(x - cam_x) * 2 < viewport / 2 and abs(y - cam_y) < viewport / 2


def get_direction(win: curses.window, x: int, y: int) -> set[str]:
    c_x, c_y = Camera.get_pos()
    viewport, _ = win.getmaxyx()

    top_cam_y = c_y - (viewport / 2)
    bottom_cam_y = c_y + (viewport / 2)
    left_cam_x = c_x - (viewport / 4)
    right_cam_x = c_x + (viewport / 4)

    directions: set[str] = set()

    if y < top_cam_y:
        directions.add("n")

    if y > bottom_cam_y:
        directions.add("s")

    if x < left_cam_x:
        directions.add("w")

    if x > right_cam_x:
        directions.add("e")

    return directions
