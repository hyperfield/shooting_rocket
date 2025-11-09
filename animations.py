import asyncio
import curses
import random
from itertools import cycle

from controls import read_controls
from garbage import random_garbage_frame
from geometry import get_frame_size
from obstacles import (Obstacle, add_obstacle, destroy_obstacle,
                       find_collision, remove_obstacle)
from settings import (GARBAGE_SPEED_RANGE, GARBAGE_SPAWN_DELAY,
                      QUIT_KEY_CODES, RESTART_KEY_CODES, ROCKET_SPEED_FACTOR,
                      SHOT_COOLDOWN_TICS, TIC_TIMEOUT)


EXPLOSION_FRAMES = [
    "  .  \n  *  \n  '  ",
    " .*. \n*###*\n .*. ",
    ".'* *'.\n *###* \n.'* *'.",
    "  '  \n . . \n'   '",
]


async def sleep(delay_time):
    if delay_time <= 0:
        await asyncio.sleep(0)
        return

    ticks = max(1, int(delay_time / TIC_TIMEOUT))
    for _ in range(ticks):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol, blink_delay):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    for _ in range(blink_delay):
        await asyncio.sleep(0)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(2)

        canvas.addstr(row, column, symbol)
        await sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(0.5)

        canvas.addstr(row, column, symbol)
        await sleep(0.3)


async def fire(canvas, start_row, start_column, coroutines, state,
               rows_speed=-0.4, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 1 < column < max_column:
        if state.restart_requested or state.quit_requested:
            break

        obstacle = find_collision(row, column)
        if obstacle:
            destroy_obstacle(obstacle)
            if getattr(obstacle, "kind", "") == "garbage":
                state.register_hit()
                center_row = obstacle.row + obstacle.rows_size / 2
                center_column = obstacle.column + obstacle.columns_size / 2
                coroutines.append(explode(canvas, center_row, center_column))
            break

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def explode(canvas, center_row, center_column):
    for frame in EXPLOSION_FRAMES:
        frame_rows, frame_columns = get_frame_size(frame)
        row = center_row - frame_rows / 2
        column = center_column - frame_columns / 2
        draw_frame(canvas, row, column, frame)
        await sleep(TIC_TIMEOUT / 2)
        draw_frame(canvas, row, column, frame, negative=True)


def update_rocket_coordinates_on_input(canvas, current_row, current_col,
                                       frame, max_y, max_x):
    (y_shift, x_shift, space_pressed,
     restart_pressed, quit_pressed) = read_controls(canvas)
    y_shift *= ROCKET_SPEED_FACTOR
    x_shift *= ROCKET_SPEED_FACTOR
    new_row = current_row + y_shift
    current_row = min(max(1, new_row), max_y)
    new_col = current_col + x_shift
    current_col = min(max(1, new_col), max_x)
    return current_row, current_col, space_pressed, restart_pressed, quit_pressed


async def animate_spaceship(canvas, rocket, current_row, current_col,
                            coroutines, state):
    """Interchanges spaceship frames."""
    margin_row, margin_col = curses.window.getmaxyx(canvas)
    # Take rocket dimensions into account
    rocket_length_offset = 10
    rocket_width_offset = 6
    max_y = margin_row - rocket_length_offset
    max_x = margin_col - rocket_width_offset
    iterator = cycle(rocket)
    shot_cooldown = 0

    for frame in iterator:
        frame_rows, frame_columns = get_frame_size(frame)
        for _ in range(2):
            if state.game_over or state.restart_requested or state.quit_requested:
                return
            (current_row, current_col, space_pressed,
             restart_pressed, quit_pressed) = \
                update_rocket_coordinates_on_input(
                    canvas, current_row, current_col, frame, max_y, max_x
                )

            if restart_pressed:
                state.request_restart()
                return

            if quit_pressed:
                state.request_quit()
                return

            if shot_cooldown:
                shot_cooldown -= 1

            if space_pressed and shot_cooldown == 0:
                shot_cooldown = SHOT_COOLDOWN_TICS
                bullet_row = current_row - 1
                bullet_column = current_col + frame_columns / 2
                coroutines.append(
                    fire(canvas, bullet_row, bullet_column, coroutines, state)
                )

            draw_frame(canvas, current_row, current_col, frame, negative=False)
            await sleep(TIC_TIMEOUT)
            draw_frame(canvas, current_row, current_col, frame, negative=True)

            obstacle = find_collision(current_row, current_col,
                                      frame_rows, frame_columns)
            if obstacle:
                destroy_obstacle(obstacle)
                state.trigger_game_over("You were hit!")
                center_row = current_row + frame_rows / 2
                center_column = current_col + frame_columns / 2
                coroutines.append(explode(canvas, center_row, center_column))
                return


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing
       if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def fly_garbage(canvas, column, garbage_frame, speed, state):
    rows_number, columns_number = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(garbage_frame)
    column = max(1, min(column, columns_number - frame_columns - 1))
    row = 1

    obstacle = Obstacle(row=row, column=column,
                        rows_size=frame_rows, columns_size=frame_columns,
                        kind="garbage")
    add_obstacle(obstacle)

    while row < rows_number and state.is_active():
        obstacle.row = row
        obstacle.column = column

        if obstacle.destroyed:
            break

        draw_frame(canvas, row, column, garbage_frame)
        await sleep(TIC_TIMEOUT)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed

    remove_obstacle(obstacle)
    draw_frame(canvas, row, column, garbage_frame, negative=True)
    if not obstacle.destroyed and state.is_active():
        state.register_miss()


async def fill_orbit_with_garbage(canvas, coroutines, state):
    delay_min, delay_max = GARBAGE_SPAWN_DELAY
    while state.is_active():
        frame = random_garbage_frame()
        _, columns_number = canvas.getmaxyx()
        _, frame_columns = get_frame_size(frame)
        column = random.randint(1, max(1, columns_number - frame_columns - 1))
        difficulty = state.difficulty_multiplier()
        speed = random.uniform(*GARBAGE_SPEED_RANGE) * difficulty
        coroutines.append(fly_garbage(canvas, column, frame, speed, state))
        await sleep(random.uniform(delay_min, delay_max) / difficulty)


async def display_hud(canvas, state):
    while not state.restart_requested and not state.quit_requested:
        _, columns = canvas.getmaxyx()
        width = max(0, columns - 4)
        best_score = state.high_scores[0] if state.high_scores else 0
        text = (
            f"Score: {state.score:04d}  Wave: {state.wave}  "
            f"Missed: {state.missed}/{state.max_misses}  Best: {best_score:04d}"
        )
        highs = ", ".join(f"{idx+1}:{score:04d}"
                          for idx, score in enumerate(state.high_scores[:3]))
        canvas.addstr(1, 2, " " * width)
        canvas.addstr(1, 2, text[:width], curses.A_BOLD)
        canvas.addstr(2, 2, " " * width)
        if highs:
            canvas.addstr(2, 2, f"High Scores → {highs}"[:width])
        await sleep(TIC_TIMEOUT)


async def watch_game_state(canvas, state, coroutines):
    while (not state.game_over and not state.restart_requested
           and not state.quit_requested):
        await sleep(TIC_TIMEOUT)

    if state.restart_requested or state.quit_requested:
        return

    state.finalize_score()
    message = state.game_over_message or "GAME OVER!"
    coroutines.append(show_game_over(canvas, message, state))
    coroutines.append(wait_for_restart(canvas, state))


async def show_game_over(canvas, message, state):
    rows, columns = canvas.getmaxyx()
    scores = state.high_scores or []
    lines = [
        message,
        "Press R to restart or Q to quit.",
        "",
        "High Scores:"
    ]
    lines.extend(f"{idx + 1}. {score:04d}" for idx, score in enumerate(scores))

    top_row = max(2, rows // 2 - len(lines) // 2)

    while not state.restart_requested and not state.quit_requested:
        for offset, text in enumerate(lines):
            column = max(2, columns // 2 - len(text) // 2)
            canvas.addstr(top_row + offset, column, " " * len(text))
            attr = curses.A_BOLD if offset == 0 else curses.A_NORMAL
            canvas.addstr(top_row + offset, column, text, attr)
        await sleep(0.5)


async def wait_for_restart(canvas, state):
    canvas.nodelay(1)
    while not state.restart_requested and not state.quit_requested:
        key = canvas.getch()
        if key in RESTART_KEY_CODES:
            state.request_restart()
            return
        if key in QUIT_KEY_CODES:
            state.request_quit()
            return
        await sleep(TIC_TIMEOUT)
