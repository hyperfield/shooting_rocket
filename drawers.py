import curses
import random
from time import sleep

from assets import get_rocket
from animations import blink, fire, animate_spaceship
from settings import TIC_TIMEOUT


def draw(canvas):
    stars = "+*.:"
    margin_col, margin_row = curses.window.getmaxyx(canvas)
    center_x, center_y = margin_col/2 - 0.1, margin_row/2
    canvas.border()
    curses.curs_set(False)
    coroutines = []

    local_max_x = margin_col - 2
    local_max_y = margin_row - 2
    for _ in range(50):
        blink_delay = random.randint(0, 10)
        x = random.randint(2, local_max_x)
        y = random.randint(2, local_max_y)
        star = random.choice(stars)
        coroutines.append(blink(canvas, x, y, star, blink_delay))
    coroutines.append(fire(canvas, center_x, center_y))

    start_row = margin_row/2 - 2
    start_col = margin_col/2
    space_pressed = False
    rocket_coroutine = animate_spaceship(canvas, get_rocket(), start_row,
                                         start_col, space_pressed)
    coroutines.append(rocket_coroutine)

    while True:
        try:
            for coroutine in coroutines.copy():
                coroutine.send(None)
                canvas.refresh()
            sleep(TIC_TIMEOUT)
        except StopIteration:
            coroutines.remove(coroutine)
