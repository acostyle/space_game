import time
import curses
import random
import asyncio


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        time.sleep(0.01)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        time.sleep(0.01)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    coroutines = []
    max_row, max_column = canvas.getmaxyx()

    for _ in range(1, 100):
        row = random.randint(1, max_row-1)
        column = random.randint(1, max_column-1)
        symbol = random.choice('+*.:')
        coroutine = blink(canvas, row=row, column=column, symbol=symbol)
        coroutines.append(coroutine)

    while True:
        coroutine = random.choice(coroutines)
        coroutine.send(None)
        canvas.border()
        canvas.refresh()


if __name__ == '__main__':
    curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw)