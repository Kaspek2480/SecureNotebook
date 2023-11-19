import curses
from time import sleep


def print_centered_from_top(stdscr, text, line, color_pair=0):
    height, width = stdscr.getmaxyx()
    x = width // 2 - len(text) // 2
    stdscr.addstr(line, x, text, curses.color_pair(color_pair))
    stdscr.refresh()


def print_centered(stdscr, text, line_from_center=0, color_pair=0):
    height, width = stdscr.getmaxyx()
    x = width // 2 - len(text) // 2
    y = height // 2 + line_from_center
    stdscr.addstr(y, x, text, curses.color_pair(color_pair))
    stdscr.refresh()


def print_center_for_time(stdscr, text, line, color_pair=0, wait_time=2):
    print_centered_from_top(stdscr, text, line, color_pair)
    stdscr.refresh()
    curses.napms(wait_time * 2000)  # Oczekiwanie w milisekundach
    print_centered_from_top(stdscr, " " * len(text), line, color_pair)
    stdscr.refresh()
