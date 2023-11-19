import curses
from datetime import datetime
from enum import Enum
from time import sleep

import database
import manager
import utils


class AuthAction(Enum):
    LOGIN = 1
    REGISTER = 2
    EXIT = 3
    ABOUT = 4


class NavigationAction(Enum):
    SUCCESS = 0
    FAILURE = 1
    EXIT = 2
    BACK = 3


class NavigationResult:
    def __init__(self, action, data=None):
        self.action = action
        self.data = data


def display_program_info(stdscr):
    # Ukrycie kursora, aby nie przeszkadzał w interakcji
    curses.curs_set(0)

    # Informacje o programie
    program_info = [
        "Witaj w SecureNotebook - bezpiecznym miejscu na Twoje notatki!",
        " ",
        "Twoje notatki są zabezpieczone przed nieautoryzowanym dostępem.",
        "Wykorzystujemy mocne szyfrowanie AES-256-CBC do ochrony treści.",
        "Klucz do odszyfrowania jest generowane z PIN-u z uzyciem KDF PBKDF2.",
        "Ta technika jest znana z menedżerów haseł, co oznacza, że jesteś w dobrych rękach.",
        " ",
        "Wersja: 1.0",
        "Naciśnij dowolny klawisz, aby opuścić ekran informacyjny."
    ]

    stdscr.clear()  # Wyczyszczenie ekranu

    # Wyśrodkowanie i wyświetlenie informacji o programie
    for i, line in enumerate(program_info):
        utils.print_centered(stdscr, line, line_from_center=i - len(program_info) // 2, color_pair=2)

    stdscr.refresh()  # Odświeżenie ekranu

    # Oczekiwanie na dowolny klawisz
    stdscr.getch()
    stdscr.clear()  # Wyczyszczenie ekranu


def draw_register_screen(stdscr):
    curses.curs_set(1)  # show cursor, so user can see where to type
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    utils.print_centered_from_top(stdscr, "SecureNotebook - Rejestracja", 0, color_pair=3)

    # get username
    utils.print_centered(stdscr, "Podaj nazwę użytkownika (max 16 znaków):", line_from_center=-2)
    username_prompt = curses.newwin(1, 21, height // 2 - 1, (width - 20) // 2)  # 20 = 16 + 4 (4 = 2x margines)
    username_prompt.addstr(0, 0, "> ")
    username_prompt.refresh()
    curses.echo()
    username_prompt.keypad(True)  # Włącz tryb KEY_PAD
    username = username_prompt.getstr(0, 2, 16).decode('utf-8')
    curses.noecho()
    username_prompt.keypad(False)  # Wyłącz tryb KEY_PAD

    # get pin, try until user enters pin which is digit only
    utils.print_centered(stdscr, "Podaj kod PIN (6 cyfr):")
    while True:
        pin_prompt = curses.newwin(1, 9, height // 2 + 1, (width - 8) // 2)
        pin_prompt.addstr(0, 0, "> ")
        pin_prompt.refresh()
        curses.echo()
        pin_prompt.keypad(True)  # Włącz tryb KEY_PAD
        pin = pin_prompt.getstr(0, 2, 6).decode('utf-8')
        curses.noecho()
        pin_prompt.keypad(False)  # Wyłącz tryb KEY_PAD

        if pin.isdigit():
            break

        curses.curs_set(0)
        utils.print_center_for_time(stdscr, "Kod PIN musi składać się z samych cyfr!", height // 2 + 3, color_pair=1,
                                    wait_time=1)
        curses.curs_set(1)
        continue

    # show summary
    stdscr.clear()
    utils.print_centered(stdscr, "Twojde dane podane przy rejestracji:", line_from_center=0)
    utils.print_centered(stdscr, f"Użytkownik: {username}", line_from_center=1, color_pair=4)
    utils.print_centered(stdscr, f"Pin: {pin}", line_from_center=2, color_pair=4)

    # wait for user to confirm
    utils.print_centered(stdscr, "Wciśnij ENTER aby potwierdzić, lub Q aby anulować", 7)
    while True:
        key = stdscr.getch()
        if key == 10:  # Enter
            if manager.create_user(username, pin):
                utils.print_center_for_time(stdscr, "Użytkownik utworzony pomyślnie!", height // 2 + 9,
                                            color_pair=2, wait_time=1)
                manager.clear_last_user()
                return
        elif key == ord('q') or key == ord('Q') or key == 27:  # ESC or Q
            return


def draw_pin_auth_screen(stdscr, user):
    curses.curs_set(0)  # Ukryj kursor
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    utils.print_centered_from_top(stdscr, "SecureNotebook - Logowanie kodem PIN", 0, color_pair=3)

    # Napis "Witaj ponownie Dawid" na środku ekranu
    utils.print_centered(stdscr, f"Witaj {user.display_name}!", line_from_center=-2)

    # Napis "wpisywanie kodu pin" na środku pod napisem powitalnym
    utils.print_centered(stdscr, "Podaj kod PIN, aby się zalogować, jeśli chcesz się wylogować wpisz 'q'",
                         line_from_center=-1)

    while True:
        height, width = stdscr.getmaxyx()
        pin_input = curses.newwin(1, 7, height // 2 + 1, width // 2 - 1)
        pin_input.keypad(True)

        pin_length = 6
        pin = ""

        # Ustawienie domyślnego miejsca dla kodu PIN
        default_pin = "_" * pin_length
        pin_input.addstr(0, 0, default_pin)

        # Początkowe ustawienie kursora na pierwszym miejscu
        cursor_position = 0
        pin_input.move(0, cursor_position)

        while True:
            stdscr.refresh()
            key = pin_input.getch()
            digit = chr(key)

            if key == 10:  # Enter
                break
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

                # check if pin is entered
                if len(pin) == pin_length:
                    pin_input.refresh()
                    break

            elif digit == 'q' or digit == 'Q' or key == 27:  # ESC or Q
                return NavigationResult(NavigationAction.FAILURE, None)
            else:
                print(
                    f"CLICK OTHER | pin: {pin}, cursor: {cursor_position}, digit: {digit} len: {len(pin)} pin_length: {pin_length} pin_input: {pin_input}")

        stdscr.refresh()

        if user.verify_pin(pin):
            utils.print_centered_from_top(stdscr, "Autoryzacja udana, ładowanie danych..", height // 2 + 6,
                                          color_pair=2)
            sleep(1)
            return NavigationResult(NavigationAction.SUCCESS, None)
        else:
            utils.print_center_for_time(stdscr, "Pin niepoprawny, spróbuj jeszcze raz", height // 2 + 6, color_pair=1,
                                        wait_time=1)


def draw_user_select_screen(stdscr, users):
    curses.curs_set(0)
    stdscr.clear()

    # Pobierz wysokość i szerokość terminala
    height, width = stdscr.getmaxyx()

    # Ustaw długość listy użytkowników (maksymalnie 5)
    user_list_length = min(len(users), 5)

    # Ustaw pozycję początkową
    start_pos = 0
    current_row = 0

    while True:
        stdscr.clear()

        # Wyświetl napis "Super Program" na górze terminala
        utils.print_centered_from_top(stdscr, "SecureNotebook - Wybór użytkownika", 0, color_pair=3)

        # Wyświetl nagłówki kolumn
        stdscr.addstr(height // 2 - 3, width // 2 - len("Nazwa użytkownika") - 5, "Nazwa użytkownika", curses.A_BOLD)
        stdscr.addstr(height // 2 - 3, width // 2 + 5, "Ostatnio widziany", curses.A_BOLD)

        currently_visible_users = users[start_pos:start_pos + user_list_length]

        # Wyświetl listę użytkowników
        i = 0
        for user in currently_visible_users:
            user_info = user.display_name
            last_visit_info = "Nieznany"
            # last_visit_info = user.last_access_timestamp.strftime("%d/%m/%Y %H:%M")

            # Podświetl aktualnie wybrany wiersz
            if i == current_row:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len("Nazwa użytkownika") - 5, user_info)
                stdscr.addstr(height // 2 - 2 + i, width // 2 + 5, last_visit_info)
                stdscr.attroff(curses.color_pair(4))
            else:
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len("Nazwa użytkownika") - 5, user_info)
                stdscr.addstr(height // 2 - 2 + i, width // 2 + 5, last_visit_info)

            i += 1

        # Wyświetl aktualną pozycję na liście
        stdscr.addstr(height - 1, 0,
                      f"Strzałki: Góra/Dół, ENTER - wybierz użytkownika, Q - wyjdź.")

        # Obsługa klawiszy
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q') or key == 27:  # ESC or Q:
            return NavigationResult(NavigationAction.BACK, None)
        elif key == curses.KEY_DOWN and current_row < user_list_length - 1:
            current_row += 1
            if current_row == user_list_length - 1 and start_pos + user_list_length < len(users):
                start_pos += 1
            print(
                f"DOWN current_row: {current_row}, start_pos: {start_pos}, user_list_length: {user_list_length}, len(users): {len(users)}")
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
            if current_row == 0 and start_pos > 0:
                start_pos -= 1
            print(
                f"UP current_row: {current_row}, start_pos: {start_pos}, user_list_length: {user_list_length}, len(users): {len(users)}")
        elif key == curses.KEY_DOWN and current_row == user_list_length - 1 and start_pos + user_list_length < len(
                users):
            start_pos += 1
            print(
                f"DOWN current_row: {current_row}, start_pos: {start_pos}, user_list_length: {user_list_length}, len(users): {len(users)}")
        elif key == curses.KEY_UP and current_row == 0 and start_pos > 0:
            start_pos -= 1
            print(
                f"UP current_row: {current_row}, start_pos: {start_pos}, user_list_length: {user_list_length}, len(users): {len(users)}")
        elif key == 10:  # ENTER key
            selected_user = users[start_pos + current_row]
            return NavigationResult(NavigationAction.SUCCESS, selected_user.user_id)
        stdscr.refresh()


def draw_main_login_screen(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    # Pobierz wysokość i szerokość terminala
    height, width = stdscr.getmaxyx()

    # Ustaw pozycję początkową
    current_row = 0

    utils.print_centered_from_top(stdscr, "SecureNotebook - Autoryzacja", 0, color_pair=3)

    # Ustaw opcje menu
    menu_options = [{"action": AuthAction.LOGIN, "text": "Zaloguj się"},
                    {"action": AuthAction.REGISTER, "text": "Zarejestruj się"},
                    {"action": AuthAction.ABOUT, "text": "O programie"},
                    {"action": AuthAction.EXIT, "text": "Wyjdź"}]

    while True:
        # Wyświetl opcje menu
        for i, option in enumerate(menu_options):
            text = option['text']
            if i == current_row:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len(text) // 2, text)
                stdscr.attroff(curses.color_pair(4))
            else:
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len(text) // 2, text)

        # Obsługa klawiszy
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == curses.KEY_DOWN and current_row < len(menu_options) - 1:
            current_row += 1
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == 10:  # ENTER key
            return menu_options[current_row]['action']

        stdscr.refresh()


def handle_auth(stdscr):
    while True:
        user_choice = draw_main_login_screen(stdscr)

        if user_choice == AuthAction.LOGIN:
            while True:

                # try to log in last user, if not possible - show user select screen
                user = manager.fetch_last_user()
                if user is not None:
                    if draw_pin_auth_screen(stdscr, user).action == NavigationAction.SUCCESS:
                        # user logged in successfully
                        return NavigationResult(NavigationAction.SUCCESS, user)

                    # user cancel auth by pressing 'q' - remove last user from db
                    manager.clear_last_user()
                    continue

                select_result = draw_user_select_screen(stdscr, manager.fetch_users())
                if select_result.action == NavigationAction.BACK:
                    break
                if select_result.data is None:
                    continue

                # user selected, show pin auth screen
                user = manager.fetch_user_by_id(str(select_result.data))
                print("Selected user: " + user.display_name)

                if draw_pin_auth_screen(stdscr, user).action == NavigationAction.SUCCESS:
                    return NavigationResult(NavigationAction.SUCCESS, user)

        elif user_choice == AuthAction.REGISTER:
            draw_register_screen(stdscr)
        elif user_choice == AuthAction.EXIT:
            exit(0)
        elif user_choice == AuthAction.ABOUT:
            display_program_info(stdscr)


sample_notes_list = [
    {"name": "Notatka 1", "favorite": True, "modification_date": datetime(2023, 1, 1, 12, 30, 0)},
    {"name": "Notatka 2", "favorite": False, "modification_date": datetime(2023, 2, 15, 9, 45, 0)},
    {"name": "Notatka 3", "favorite": True, "modification_date": datetime(2023, 3, 20, 15, 0, 0)},
    {"name": "Notatka 4", "favorite": False, "modification_date": datetime(2023, 4, 5, 18, 20, 0)},
    {"name": "Notatka 5", "favorite": True, "modification_date": datetime(2023, 5, 10, 10, 0, 0)},
    {"name": "Notatka 6", "favorite": False, "modification_date": datetime(2023, 6, 25, 14, 30, 0)},
    {"name": "Notatka 7", "favorite": True, "modification_date": datetime(2023, 7, 8, 8, 45, 0)},
    {"name": "Notatka 8", "favorite": False, "modification_date": datetime(2023, 8, 18, 16, 15, 0)},
    {"name": "Notatka 9", "favorite": True, "modification_date": datetime(2023, 9, 22, 11, 0, 0)},
    {"name": "Notatka 10", "favorite": False, "modification_date": datetime(2023, 10, 30, 13, 45, 0)},
]


from utils import print_centered_from_top, print_centered


def display_notes_list(stdscr, notes_list):
    curses.curs_set(0)  # Ustawienie widoczności kursora na 0

    stdscr.clear()  # Wyczyszczenie ekranu

    # Nagłówek
    header = "Lista Notatek"
    print_centered_from_top(stdscr, header, line=0, color_pair=1)

    # Wysokość i szerokość okna
    height, width = stdscr.getmaxyx()

    # Początkowa pozycja dla kafelków
    start_y = 2

    # Szerokość kafelka
    tile_width = width - 4

    # Wyświetlanie kafelków dla każdej notatki
    for note in notes_list:
        name = note["name"]
        favorite = note["favorite"]
        modification_date = note["modification_date"]

        # Jeśli notatka jest oznaczona jako ulubiona, kolor obwódki to zielony, inaczej biały
        border_color = 3 if favorite else 1

        # Formatowanie daty modyfikacji w czytelny sposób
        modification_date_str = modification_date.strftime("%Y-%m-%d %H:%M:%S")

        # Formatowanie i wyświetlanie kafelka
        tile = f"{name[:tile_width-2]:<{tile_width-2}}"

        # Rysowanie obwódki wokół kafelka
        stdscr.attron(curses.color_pair(border_color))
        stdscr.addstr(start_y, 2, f" {tile} ", curses.color_pair(border_color))
        stdscr.attroff(curses.color_pair(border_color))

        start_y += 2  # Zwiększanie pozycji dla kolejnego kafelka

    stdscr.refresh()  # Odświeżenie ekranu
    stdscr.getch()  # Oczekiwanie na dowolny klawisz


def main(stdscr):
    database.init()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Przykładowa para kolorów (tekst na niebieskim tle)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Przykładowa para kolorów (tekst na niebieskim tle)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # curses.curs_set(0)  # Ukryj kursor
    stdscr.clear()

    display_notes_list(stdscr, sample_notes_list)

    auth_result = handle_auth(stdscr)

    # print_user_list(stdscr, users)

    # Po wyjściu z pętli, czyść ekran i wyświetl komunikat powitalny
    stdscr.clear()
    stdscr.addstr(2, 2, f"Witaj, użytkowniku {auth_result.data.display_name}!")
    stdscr.refresh()

    # Czekaj na klawisz przed zamknięciem programu
    stdscr.getch()


curses.wrapper(main)
