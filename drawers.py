import curses
import random
from time import sleep

from assets import rocket
from animations import blink, fire, animate_spaceship
from settings import TIC_TIMEOUT


def draw(canvas):
    stars = "+*.:"
    max_x, max_y = curses.window.getmaxyx(canvas)
    center_x, center_y = max_x/2 - 0.1, max_y/2
    canvas.border()
    curses.curs_set(False)
    coroutines = []

    local_max_x = max_x - 2
    local_max_y = max_y - 2
    for _ in range(50):
        blink_delay = random.randint(0, 10)
        x = random.randint(2, local_max_x)
        y = random.randint(2, local_max_y)
        star = random.choice(stars)
        coroutines.append(blink(canvas, x, y, star, blink_delay))
    coroutines.append(fire(canvas, center_x, center_y))

    start_row = max_y/2 - 2
    start_col = max_x/2
    space_pressed = False
    r_coroutine = animate_spaceship(canvas, rocket(), start_row,
                                    start_col, space_pressed)
    coroutines.append(r_coroutine)

    while True:
        try:
            for coroutine in coroutines.copy():
                coroutine.send(None)
                canvas.refresh()
            sleep(TIC_TIMEOUT)
        except StopIteration:
            coroutines.remove(coroutine)
