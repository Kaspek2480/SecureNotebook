import curses
from datetime import datetime


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
    curses.napms(wait_time * 1000)  # Oczekiwanie w milisekundach
    print_centered_from_top(stdscr, " " * len(text), line, color_pair)
    stdscr.refresh()


def print_ascii_art(stdscr, text, line_from_center=0, color_pair=0):
    height, width = stdscr.getmaxyx()
    x = width // 2 - len(text[0]) // 2
    y = height // 2 + line_from_center
    for line in text:
        print(x, y, line)
        stdscr.addstr(y, x, line, curses.color_pair(color_pair))
        y += 1
    stdscr.refresh()


def timestamp_to_date(timestamp):
    if timestamp is None:
        return "Nigdy"
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp)

    # Format the datetime object as a string
    date_string = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    return date_string
