import asyncio
import curses
from itertools import cycle
import random
from time import sleep


TIC_TIMEOUT = 0.1
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple with controls state."""

    canvas.nodelay(1)
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def get_rocket():
    rocket_frames = []
    for i in range(1, 3):
        with open(f"frames/rocket_frame_{i}.txt", "r") as my_file:
            rocket_frames.append(my_file.read())
    return rocket_frames


async def blink(canvas, row, column, symbol, blink_delay):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    canvas.refresh()
    for _ in range(blink_delay):
        await asyncio.sleep(0)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(int(2/TIC_TIMEOUT)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(int(0.3/TIC_TIMEOUT)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(int(0.5/TIC_TIMEOUT)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(int(0.3/TIC_TIMEOUT)):
            await asyncio.sleep(0)


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


async def animate_spaceship(canvas, rocket, column, row, space_pressed):
    """Interchanges spaceship frames."""
    max_y, max_x = curses.window.getmaxyx(canvas)
    # Take rocket dimensions into account
    max_y -= 10
    max_x -= 6
    iterator = cycle(rocket)
    for frame in iterator:
        y_shift, x_shift, space_pressed = read_controls(canvas)
        new_row = row + y_shift
        if (1 <= new_row <= max_y):
            row = new_row
        new_col = column + x_shift
        if (1 <= new_col <= max_x):
            column = new_col
        draw_frame(canvas, row, column, frame)
        canvas.refresh()
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)
        canvas.refresh()


def draw(canvas):
    stars = "+*.:"
    rocket = get_rocket()
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
    r_coroutine = animate_spaceship(canvas, rocket, start_row,
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


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
