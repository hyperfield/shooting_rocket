import asyncio
import curses
from itertools import cycle

from settings import TIC_TIMEOUT, ROCKET_SPEED_FACTOR
from controls import read_controls


async def sleep(delay_time):
    for _ in range(int(delay_time/TIC_TIMEOUT)):
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


def update_rocket_coordinates_on_input(canvas, current_row, current_col,
                                       frame, max_y, max_x):
    y_shift, x_shift, space_pressed = read_controls(canvas)
    y_shift *= ROCKET_SPEED_FACTOR
    x_shift *= ROCKET_SPEED_FACTOR
    new_row = current_row + y_shift
    current_row = min(max(1, new_row), max_y)
    new_col = current_col + x_shift
    current_col = min(max(1, new_col), max_x)
    return current_row, current_col


async def animate_spaceship(canvas, rocket, current_col, current_row):
    """Interchanges spaceship frames."""
    margin_row, margin_col = curses.window.getmaxyx(canvas)
    # Take rocket dimensions into account
    rocket_length_offset = 10
    rocket_width_offset = 6
    max_y = margin_row - rocket_length_offset
    max_x = margin_col - rocket_width_offset
    iterator = cycle(rocket)
    for frame in iterator:
        for _ in range(2):
            current_row, current_col = update_rocket_coordinates_on_input(
                                                    canvas, current_row,
                                                    current_col, frame,
                                                    max_y, max_x
                                                    )
            draw_frame(canvas, current_row, current_col, frame, negative=False)
            await sleep(TIC_TIMEOUT)
            draw_frame(canvas, current_row, current_col, frame, negative=True)


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
