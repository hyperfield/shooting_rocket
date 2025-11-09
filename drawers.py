import curses
import random
from time import sleep

from assets import get_rocket_frames
from animations import (animate_spaceship, blink, display_hud,
                        fill_orbit_with_garbage, watch_game_state)
from game_state import GameState
from settings import MAX_MISSES, TIC_TIMEOUT, WAVE_SIZE


def draw(canvas):
    stars = "+*.:"
    curses.curs_set(False)

    while True:
        canvas.clear()
        canvas.border()
        margin_col, margin_row = curses.window.getmaxyx(canvas)
        coroutines = []

        x_margin_offset = 2
        y_margin_offset = 2
        local_max_x = margin_col - x_margin_offset
        local_max_y = margin_row - y_margin_offset
        for _ in range(50):
            blink_delay = random.randint(0, 10)
            x = random.randint(x_margin_offset, max(x_margin_offset, local_max_x))
            y = random.randint(y_margin_offset, max(y_margin_offset, local_max_y))
            star = random.choice(stars)
            coroutines.append(blink(canvas, x, y, star, blink_delay))

        start_row = margin_row / 2 - y_margin_offset
        start_col = margin_col / 2
        state = GameState(MAX_MISSES, WAVE_SIZE)
        rocket_coroutine = animate_spaceship(
            canvas, get_rocket_frames(),
            start_row, start_col, coroutines, state
            )
        coroutines.append(rocket_coroutine)
        coroutines.append(fill_orbit_with_garbage(canvas, coroutines, state))
        coroutines.append(display_hud(canvas, state))
        coroutines.append(watch_game_state(canvas, state, coroutines))

        while not state.restart_requested and not state.quit_requested:
            for coroutine in coroutines.copy():
                try:
                    coroutine.send(None)
                except StopIteration:
                    coroutines.remove(coroutine)
            canvas.refresh()
            sleep(TIC_TIMEOUT)

        if state.quit_requested:
            return
