from settings import (DIRECTION_HOLD_TICKS, DOWN_KEY_CODE, LEFT_KEY_CODE,
                      QUIT_KEY_CODES, RESTART_KEY_CODES, RIGHT_KEY_CODE,
                      SPACE_KEY_CODE, UP_KEY_CODE)


_rows_direction = 0
_columns_direction = 0
_row_hold = 0
_column_hold = 0


def _apply_row(direction):
    global _rows_direction, _row_hold
    _rows_direction = direction
    _row_hold = DIRECTION_HOLD_TICKS


def _apply_column(direction):
    global _columns_direction, _column_hold
    _columns_direction = direction
    _column_hold = DIRECTION_HOLD_TICKS


def _decay_direction(has_row_event, has_column_event):
    global _row_hold, _column_hold, _rows_direction, _columns_direction
    if not has_row_event and _row_hold > 0:
        _row_hold -= 1
        if _row_hold == 0:
            _rows_direction = 0
    if not has_column_event and _column_hold > 0:
        _column_hold -= 1
        if _column_hold == 0:
            _columns_direction = 0


def read_controls(canvas):
    """Read keys pressed and returns tuple with controls state."""

    canvas.nodelay(1)
    space_pressed = False
    restart_pressed = False
    quit_pressed = False
    row_event = False
    column_event = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            _apply_row(-1)
            row_event = True
            continue

        if pressed_key_code == DOWN_KEY_CODE:
            _apply_row(1)
            row_event = True
            continue

        if pressed_key_code == RIGHT_KEY_CODE:
            _apply_column(1)
            column_event = True
            continue

        if pressed_key_code == LEFT_KEY_CODE:
            _apply_column(-1)
            column_event = True
            continue

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
            continue

        if pressed_key_code in RESTART_KEY_CODES:
            restart_pressed = True
            continue

        if pressed_key_code in QUIT_KEY_CODES:
            quit_pressed = True

    _decay_direction(row_event, column_event)
    return (_rows_direction, _columns_direction,
            space_pressed, restart_pressed, quit_pressed)
