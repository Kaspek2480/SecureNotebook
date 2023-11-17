import curses


def print_center(stdscr, text, line, color_pair=0):
    height, width = stdscr.getmaxyx()
    x = width // 2 - len(text) // 2
    stdscr.addstr(line, x, text, curses.color_pair(color_pair))
    stdscr.refresh()
