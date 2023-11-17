import curses

import utils


def get_user_pin(stdscr):
    height, width = stdscr.getmaxyx()
    pin_input = curses.newwin(1, 7, height // 2 + 2, width // 2 - 2)
    pin_input.keypad(True)

    pin_length = 6
    pin = ""

    # Ustawienie domyślnego miejsca dla kodu PIN
    default_pin = "_" * pin_length
    pin_input.addstr(0, 0, default_pin)

    # Początkowe ustawienie kursora na pierwszym miejscu
    cursor_position = 0
    pin_input.move(0, cursor_position)

    terminate = False
    while terminate is False:
        stdscr.refresh()
        key = pin_input.getch()
        digit = chr(key)

        if key == 10:  # Enter
            terminate = True
            print("ENTER")
        elif key == 8:  # Backspace
            if cursor_position > 0:
                cursor_position -= 1
                pin_input.move(0, cursor_position)
                pin_input.addstr(0, cursor_position, '_')
                pin = pin[:-1]
        elif digit.isdigit() and len(pin) < pin_length:
            pin += digit
            pin_input.addstr(0, cursor_position, '*')
            cursor_position += 1

            print(f"CLICK | pin: {pin}, cursor: {cursor_position}, digit: {digit} len: {len(pin)} pin_length: {pin_length} pin_input: {pin_input}")

            # check if pin is entered
            if len(pin) == pin_length:
                pin_input.clear()
                pin_input.addstr(pin)
                print("PIN ENTERED 1")
                terminate = True

        else:
            print(f"CLICK OTHER | pin: {pin}, cursor: {cursor_position}, digit: {digit} len: {len(pin)} pin_length: {pin_length} pin_input: {pin_input}")

    stdscr.refresh()
    stdscr.getch()
    return pin


def verify_pin_animation(stdscr, pin):
    curses.curs_set(0)  # Ukryj kursor
    height, width = stdscr.getmaxyx()

    if pin == "123456":
        success_message = "Pin poprawny!"
        utils.print_center(stdscr, success_message, height // 2 + 6)
    else:
        error_message = "Pin niepoprawny!"
        utils.print_center(stdscr, error_message, height // 2 + 6, color_pair=1)

    stdscr.refresh()


def draw_login_screen(stdscr):
    curses.curs_set(0)  # Ukryj kursor
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Napis "Witaj ponownie Dawid" na środku ekranu
    welcome_message = "Witaj ponownie Dawid"
    stdscr.addstr(height // 2 - 2, width // 2 - len(welcome_message) // 2, welcome_message)

    # Napis "wpisywanie kodu pin" na środku pod napisem powitalnym
    pin_prompt = "Podaj kod PIN, aby się zalogować, jeśli chcesz się wylogować wpisz 'q'"
    stdscr.addstr(height // 2, width // 2 - len(pin_prompt) // 2, pin_prompt)

    pin = get_user_pin(stdscr)
    print(f"Pin: {pin}")
    # verify_pin_animation(stdscr, pin)

    return pin


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Przykładowa para kolorów (tekst na niebieskim tle)
    curses.curs_set(0)  # Ukryj kursor
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    pin_input = draw_login_screen(stdscr)

    # Po wyjściu z pętli, czyść ekran i wyświetl komunikat powitalny
    stdscr.clear()
    stdscr.addstr(2, 2, f"Witaj, użytkowniku test!")
    stdscr.refresh()

    # Czekaj na klawisz przed zamknięciem programu
    stdscr.getch()


curses.wrapper(main)
