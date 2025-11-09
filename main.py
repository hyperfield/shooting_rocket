#!/usr/bin/env python3

import curses

from drawers import draw


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
