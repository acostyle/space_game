import time
import curses
import random
import asyncio
import os
from itertools import cycle
from curses_tools import draw_frame, get_frame_size, read_controls
from space_garbage import fly_garbage

BORDER = 1
TIC_TIMEOUT = 0.1
SYMBOLS = '+*.:'
STARS_AMOUNT = 100
GARBAGE_AMOUNT = 25
COROUTINES = []


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

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

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column, max_row, max_column, *frames):
    """Display animation of rocket."""

    frame_rows, frame_columns = get_frame_size(frames[0])
    for frame in cycle(frames):
        row_direction, column_direction, space_button = read_controls(canvas)

        row += row_direction
        column += column_direction

        if row <= 0:
            row = 1
        if row + frame_rows >= max_row:
            row = max_row - frame_rows - BORDER
        if column <= 0:
            column = 1
        if column + frame_columns >= max_column:
            column = max_column - frame_columns - BORDER

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


async def blink(canvas, row, column, symbol='*'):
    """Display animation of stars."""

    await sleep(random.randint(0, 10))

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


def get_random_coordinates(max_row, max_column):
    """Get random star coordinates."""

    return random.randint(1, max_row - 2), random.randint(1, max_column - 2)


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def get_frames_from_files(frames_dir):
    """Get frames."""
    frames = []
    for frame_file in os.listdir(f'{frames_dir}'):
        with open(f'{frames_dir}/{frame_file}') as _file:
            frames.append(_file.read())

    return frames


async def fill_orbit_with_garbage(canvas, max_column, offset_tics, garbage_frames):
    while True:
        await sleep(offset_tics)

        COROUTINES.append(
            fly_garbage(
                canvas,
                random.randint(1, max_column),
                random.choice(garbage_frames),
            )
        )


def draw(canvas):
    """Draw game."""

    max_row, max_column = canvas.getmaxyx()

    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    COROUTINES.extend(
        [
            blink(
                canvas,
                *get_random_coordinates(max_row, max_column),
                random.choice(SYMBOLS)
            )
            for _ in range(STARS_AMOUNT)
        ]
    )
    # COROUTINES.extend(fire(canvas, max_row//2, max_column//2 + 2))

    rocket_frames = get_frames_from_files('rocket_frames')
    COROUTINES.append(
        animate_spaceship(
            canvas,
            max_row // 2,
            max_column // 2,
            max_row,
            max_column,
            *rocket_frames,
        )
    )

    garbage_frames = get_frames_from_files('trash_frames')
    offset_tics = 25
    COROUTINES.append(
        fill_orbit_with_garbage(
            canvas,
            max_column,
            offset_tics,
            garbage_frames,
        )
    )
    while COROUTINES:
        for coroutine in COROUTINES:
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
