import curses

import cli_controller


def main(stdscr):
    cli_controller.start(stdscr)


curses.wrapper(main)