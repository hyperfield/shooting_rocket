import asyncio
import curses
from itertools import cycle

from settings import TIC_TIMEOUT, ROCKET_SPEED_FACTOR
from controls import read_controls


async def run_time_delay(delay_time):
    for _ in range(int(delay_time/TIC_TIMEOUT)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol, blink_delay):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    for _ in range(blink_delay):
        await asyncio.sleep(0)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await run_time_delay(2)

        canvas.addstr(row, column, symbol)
        await run_time_delay(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await run_time_delay(0.5)

        canvas.addstr(row, column, symbol)
        await run_time_delay(0.3)


async def fire(canvas, start_row, start_column, rows_speed=-0.4,
               columns_speed=0):
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
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, rocket, col, row, space_pressed):
    """Interchanges spaceship frames."""
    margin_row, margin_col = curses.window.getmaxyx(canvas)
    # Take rocket dimensions into account
    max_y = margin_row - 10
    max_x = margin_col - 6
    iterator = cycle(rocket)
    for frame in iterator:
        y_shift, x_shift, space_pressed = read_controls(canvas)
        y_shift *= ROCKET_SPEED_FACTOR
        x_shift *= ROCKET_SPEED_FACTOR
        new_row = row + y_shift
        if (1 <= new_row <= max_y):
            row = new_row
        elif new_row < 1:
            row = 1
        else:
            row = max_y
        new_col = col + x_shift
        if (1 <= new_col <= max_x):
            col = new_col
        elif new_col < 1:
            col = 1
        else:
            col = max_x
        draw_frame(canvas, row, col, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, col, frame, negative=True)


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
