import curses
import random
from time import sleep

from assets import get_rocket_frames
from animations import blink, fire, animate_spaceship
from settings import TIC_TIMEOUT


def draw(canvas):
    stars = "+*.:"
    margin_col, margin_row = curses.window.getmaxyx(canvas)
    center_x, center_y = margin_col / 2, margin_row / 2
    canvas.border()
    curses.curs_set(False)
    coroutines = []

    x_margin_offset = 2
    y_margin_offset = 2
    local_max_x = margin_col - x_margin_offset
    local_max_y = margin_row - y_margin_offset
    for _ in range(50):
        blink_delay = random.randint(0, 10)
        x = random.randint(2, local_max_x)
        y = random.randint(2, local_max_y)
        star = random.choice(stars)
        coroutines.append(blink(canvas, x, y, star, blink_delay))
    coroutines.append(fire(canvas, center_x, center_y))

    start_row = margin_row / 2 - y_margin_offset
    start_col = margin_col / 2
    rocket_coroutine = animate_spaceship(
        canvas, get_rocket_frames(),
        start_row, start_col
        )
    coroutines.append(rocket_coroutine)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        sleep(TIC_TIMEOUT)
