import sys
from os.path import abspath, dirname

# Add the 'shared' directory to the Python path
sys.path.append(abspath(dirname(dirname(__file__))))

from enum import Enum
from cli_utils import *
from shared.database import init
from shared.manager import *


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
    # hide cursor
    curses.curs_set(0)

    program_info = [
        "Witaj w SecureNotebook - bezpiecznym miejscu na Twoje notatki!",
        " ",
        "Twoje notatki są zabezpieczone przed nieautoryzowanym dostępem.",
        "Wykorzystujemy mocne szyfrowanie AES-256-CBC do ochrony treści.",
        "Klucz do odszyfrowania jest generowany z PIN-u z uzyciem KDF PBKDF2.",
        "Ta technika jest znana z menedżerów haseł, co oznacza, że jesteś w dobrych rękach.",
        " ",
        "Wersja: 1.0",
        "Naciśnij dowolny klawisz, aby opuścić ekran informacyjny."
    ]

    stdscr.clear()

    # center the text
    for i, line in enumerate(program_info):
        print_centered(stdscr, line, line_from_center=i - len(program_info) // 2, color_pair=2)

    stdscr.refresh()
    stdscr.getch()  # wait for user to press any key
    stdscr.clear()


def draw_register_screen(stdscr):
    curses.curs_set(1)  # show cursor, so user can see where to type
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    print_centered_from_top(stdscr, "SecureNotebook - Rejestracja", 0, color_pair=3)

    # get username
    print_centered(stdscr, "Podaj nazwę użytkownika (max 16 znaków):", line_from_center=-2)
    username_prompt = curses.newwin(1, 21, height // 2 - 1, (width - 20) // 2)  # 20 = 16 + 4 (4 = 2x margines)
    username_prompt.addstr(0, 0, "> ")
    username_prompt.refresh()
    curses.echo()
    username_prompt.keypad(True)  # enable KEY_PAD mode to handle special keys
    username = username_prompt.getstr(0, 2, 16).decode('utf-8')
    curses.noecho()
    username_prompt.keypad(False)  # disable KEY_PAD mode

    # get pin, try until user enters pin which is digit only
    print_centered(stdscr, "Podaj kod PIN (6 cyfr):")
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

        print_center_for_time(stdscr, "Kod PIN musi składać się z samych cyfr!", height // 2 + 3, color_pair=1,
                              wait_time=1)
        continue

    # show summary
    curses.curs_set(0)
    stdscr.refresh()
    stdscr.clear()

    print_centered(stdscr, "Twoje dane podane przy rejestracji:", line_from_center=0)
    print_centered(stdscr, f"Użytkownik: {username}", line_from_center=1, color_pair=4)
    print_centered(stdscr, f"Pin: {pin}", line_from_center=2, color_pair=4)

    # wait for user to confirm
    print_centered(stdscr, "Wciśnij ENTER aby potwierdzić, lub Q aby anulować", 7)
    while True:
        key = stdscr.getch()
        if key == 10:  # Enter
            if create_user(username, pin):
                print_center_for_time(stdscr, "Użytkownik utworzony pomyślnie!", height // 2 + 9,
                                      color_pair=2, wait_time=1)
                clear_last_user()
                return
        elif key == ord('q') or key == ord('Q') or key == 27:  # ESC or Q
            return


def draw_pin_auth_screen(stdscr, user):
    curses.curs_set(0)  # hide cursor
    stdscr.clear()

    print_centered_from_top(stdscr, "SecureNotebook - Logowanie kodem PIN", 0, color_pair=3)

    print_centered(stdscr, f"Witaj {user.display_name}!", line_from_center=-2)
    print_centered(stdscr, "Podaj kod PIN, aby się zalogować, jeśli chcesz się wylogować wpisz 'q'",
                   line_from_center=-1)

    while True:
        height, width = stdscr.getmaxyx()
        pin_input = curses.newwin(1, 7, height // 2 + 1, width // 2 - 1)
        pin_input.keypad(True)

        pin_length = 6
        pin = ""

        # default_pin = "______"
        default_pin = "_" * pin_length
        pin_input.addstr(0, 0, default_pin)

        cursor_position = 0
        pin_input.move(0, cursor_position)

        # get pin from user, digit by digit
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

        stdscr.refresh()

        if verify_user_pin(user, pin):
            initialize_user(user, pin)
            print_center_for_time(stdscr, "Autoryzacja udana, ładowanie danych..", height // 2 + 6, color_pair=2,
                                  wait_time=1)
            return NavigationResult(NavigationAction.SUCCESS, None)
        else:
            print_center_for_time(stdscr, "Pin niepoprawny, spróbuj jeszcze raz", height // 2 + 6, color_pair=1,
                                  wait_time=1)


def draw_user_select_screen(stdscr, users):
    curses.curs_set(0)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    # set user list length (max 5)
    user_list_max_length = min(len(users), 5)

    # set initial position
    start_pos = 0
    current_row = 0

    while True:
        stdscr.clear()

        print_centered_from_top(stdscr, "SecureNotebook - Wybór użytkownika", 0, color_pair=3)

        # display column headers
        stdscr.addstr(height // 2 - 3, width // 2 - len("Nazwa użytkownika") - 5, "Nazwa użytkownika", curses.A_BOLD)
        stdscr.addstr(height // 2 - 3, width // 2 + 5, "Ostatnio widziany", curses.A_BOLD)

        currently_visible_users = users[start_pos:start_pos + user_list_max_length]

        # display users
        i = 0
        for user in currently_visible_users:
            user_info = user.display_name
            last_visit_info = timestamp_to_date(user.last_access_timestamp)

            # highlight currently selected row
            if i == current_row:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len("Nazwa użytkownika") - 5, user_info)
                stdscr.addstr(height // 2 - 2 + i, width // 2 + 5, last_visit_info)
                stdscr.attroff(curses.color_pair(4))
            else:
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len("Nazwa użytkownika") - 5, user_info)
                stdscr.addstr(height // 2 - 2 + i, width // 2 + 5, last_visit_info)

            i += 1

        # display current position on the list
        stdscr.addstr(height - 1, 0,
                      f"Strzałki: Góra/Dół, ENTER - wybierz użytkownika, Q - wyjdź.")

        # key handling
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q') or key == 27:  # ESC or Q:
            return NavigationResult(NavigationAction.BACK, None)
        elif key == curses.KEY_DOWN and current_row < user_list_max_length - 1:
            current_row += 1
            if current_row == user_list_max_length - 1 and start_pos + user_list_max_length < len(users):
                start_pos += 1
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
            if current_row == 0 and start_pos > 0:
                start_pos -= 1
        elif key == curses.KEY_DOWN and current_row == user_list_max_length - 1 and start_pos + user_list_max_length < len(
                users):
            start_pos += 1
        elif key == curses.KEY_UP and current_row == 0 and start_pos > 0:
            start_pos -= 1
        elif key == 10:  # ENTER key
            selected_user = users[start_pos + current_row]
            return NavigationResult(NavigationAction.SUCCESS, selected_user.user_id)
        stdscr.refresh()


def draw_main_login_screen(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    # set initial position
    current_row = 0

    print_centered_from_top(stdscr, "SecureNotebook - Autoryzacja", 0, color_pair=3)

    menu_options = [
        {"action": AuthAction.LOGIN, "text": "Zaloguj się"},
        {"action": AuthAction.REGISTER, "text": "Zarejestruj się"},
        {"action": AuthAction.ABOUT, "text": "O programie"},
        {"action": AuthAction.EXIT, "text": "Wyjdź"}
    ]

    while True:
        # display menu options
        for i, option in enumerate(menu_options):
            text = option['text']
            if i == current_row:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len(text) // 2, text)
                stdscr.attroff(curses.color_pair(4))
            else:
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len(text) // 2, text)

        # key handling
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


def draw_notes_select_screen(stdscr, user):
    curses.curs_set(0)
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    refresh = False
    notes = fetch_user_notes(user.user_id)

    # set list length (max 7)
    note_list_length = min(len(notes), 7)

    start_pos = 0
    current_row = 0

    while True:
        # in case user added new note / added to favourite, refresh notes list
        if refresh:
            start_pos = 0
            current_row = 0
            notes = fetch_user_notes(user.user_id)
            refresh = False

        stdscr.clear()

        print_centered_from_top(stdscr, "SecureNotebook - Notatki", 0, color_pair=3)

        note_title_text = "Nazwa notatki"
        last_edit_text = "Ostatnia edycja"

        # display column headers
        stdscr.addstr(height // 2 - 3, width // 2 - len(note_title_text) - 5, note_title_text, curses.A_BOLD)
        stdscr.addstr(height // 2 - 3, width // 2 + 5, last_edit_text, curses.A_BOLD)

        currently_visible_notes = notes[start_pos:start_pos + note_list_length]

        i = 0
        for note in currently_visible_notes:
            note_title = note.title
            last_edit_info = timestamp_to_date(note.last_modify_timestamp)
            if note.favorite:
                note_title = "★ " + note_title
            else:
                note_title = "  " + note_title

            # highlight currently selected row
            if i == current_row:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len(note_title_text) - 5, note_title)
                stdscr.addstr(height // 2 - 2 + i, width // 2 + 5, str(last_edit_info))
                stdscr.attroff(curses.color_pair(4))
            else:
                stdscr.addstr(height // 2 - 2 + i, width // 2 - len(note_title_text) - 5, note_title)
                stdscr.addstr(height // 2 - 2 + i, width // 2 + 5, str(last_edit_info))

            i += 1

        # display current position on the list
        stdscr.addstr(height - 1, 0,
                      f"Strzałki: Góra/Dół, ENTER - wybierz, N - nowa, D - usuń, "
                      f"F - ulubiona, Q - wyjdź, L - wyloguj")

        # key handling
        key = stdscr.getch()

        current_note = None
        if len(notes) > 0:
            current_note = notes[start_pos + current_row]

        if key == ord('q') or key == ord('Q') or key == 27:  # ESC or Q:
            return NavigationResult(NavigationAction.EXIT, None)
        elif key == curses.KEY_DOWN and current_row < note_list_length - 1:
            current_row += 1
            if current_row == note_list_length - 1 and start_pos + note_list_length < len(notes):
                start_pos += 1
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
            if current_row == 0 and start_pos > 0:
                start_pos -= 1
        elif key == curses.KEY_DOWN and current_row == note_list_length - 1 and start_pos + note_list_length < len(
                notes):
            start_pos += 1
        elif key == curses.KEY_UP and current_row == 0 and start_pos > 0:
            start_pos -= 1
        elif key == 10:  # ENTER key
            return NavigationResult(NavigationAction.SUCCESS, current_note)
        elif key == ord('f') or key == ord('F'):  # add to favourite
            current_note.favorite = not current_note.favorite
            update_note(current_note)

            refresh = True
        elif key == ord('n') or key == ord('N'):  # new note
            note_name = get_note_name_screen(stdscr)
            created_note = Note(title=note_name.data)
            ensure_encrypted_note(created_note)
            user.update_note(created_note)

            refresh = True
        elif key == ord('l') or key == ord('L'):  # log out
            return NavigationResult(NavigationAction.BACK, None)
        elif key == ord('d') or key == ord('D'):  # delete note
            curses.curs_set(0)
            stdscr.refresh()
            stdscr.clear()

            print_centered(stdscr, "Czy na pewno chcesz usunąć notatkę?", line_from_center=0)
            print_centered(stdscr, "Wciśnij ENTER aby potwierdzić, lub Q aby anulować", 1)

            while True:
                key = stdscr.getch()
                if key == 10:
                    user.remove_note(current_note)
                    refresh = True
                    break
                elif key == ord('q') or key == ord('Q') or key == 27:  # ESC or Q
                    break

        stdscr.refresh()


def get_note_name_screen(stdscr):
    curses.curs_set(1)  # show cursor, so user can see where to type
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    print_centered_from_top(stdscr, "SecureNotebook - Nowa notatka", 0, color_pair=3)

    print_centered(stdscr, "Podaj nazwę notatki (max 16 znaków):", line_from_center=-2)
    note_prompt = curses.newwin(1, 21, height // 2 - 1, (width - 20) // 2)  # 20 = 16 + 4 (4 = 2x margines)
    note_prompt.addstr(0, 0, "> ")
    note_prompt.refresh()
    curses.echo()

    note_prompt.keypad(True)  # enable KEY_PAD mode to handle special keys
    note_name = note_prompt.getstr(0, 2, 16).decode('utf-8')
    curses.noecho()
    note_prompt.keypad(False)  # disable KEY_PAD mode

    return NavigationResult(NavigationAction.SUCCESS, note_name)


def draw_note_edit_screen(stdscr, note):
    curses.curs_set(1)  # hide cursor
    curses.noecho()  # do not show typed characters (we will handle it manually)
    curses.cbreak()  # enable instant key input (no need to press Enter)
    stdscr.keypad(True)  # enable KEY_PAD mode to handle special keys

    current_line = 0
    cursor_x = 0
    scroll_offset = 0

    note_lines = note.content.split("\n")

    while True:
        stdscr.clear()

        for i, line in enumerate(note_lines[scroll_offset:]):
            stdscr.addstr(i, 0, line)

        # display title and shortcuts
        title_str = "Tytuł: " + note.title
        stdscr.addstr(curses.LINES - 1, 0, title_str, curses.color_pair(2))
        shortcuts_str = " | CTRL+S - zapisz, CTRL+E - powrót"
        stdscr.addstr(curses.LINES - 1, len(title_str), shortcuts_str, curses.A_DIM)

        stdscr.move(current_line, cursor_x)
        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_line = max(0, current_line - 1)
            if current_line < scroll_offset:
                scroll_offset = current_line
        elif key == curses.KEY_DOWN:
            current_line = min(len(note_lines) - 1, current_line + 1)
            if current_line >= scroll_offset + curses.LINES - 1:
                scroll_offset = current_line - curses.LINES + 2
        elif key == curses.KEY_LEFT:
            cursor_x = max(0, cursor_x - 1)
        elif key == curses.KEY_RIGHT:
            if len(note_lines[current_line]) - 1 >= curses.COLS:
                continue
            if current_line < len(note_lines):
                cursor_x = min(len(note_lines[current_line]), cursor_x + 1)

        elif key == 10:  # Enter
            # check if maximum number of lines is reached
            if len(note_lines) >= curses.LINES - 1:
                continue

            # add new line
            note_lines.insert(current_line + 1, "")
            current_line += 1
            cursor_x = 0
        elif key == 27:  # Escape
            break
        elif key == 127:  # Backspace
            # remove character at current position
            if cursor_x > 0 or current_line > 0:
                if cursor_x == 0:
                    # append current line to previous line
                    cursor_x = len(note_lines[current_line - 1])
                    note_lines[current_line - 1] += note_lines.pop(current_line)
                    current_line -= 1
                    if current_line < scroll_offset:
                        scroll_offset = current_line
                else:
                    note_lines[current_line] = (
                            note_lines[current_line][:cursor_x - 1]
                            + note_lines[current_line][cursor_x:]
                    )
                    cursor_x -= 1
        elif key == curses.KEY_DC:  # DEL
            # delete character at current position
            if cursor_x < len(note_lines[current_line]) or current_line < len(note_lines) - 1:
                if cursor_x == len(note_lines[current_line]):
                    # Dołącz kolejną linię do aktualnej linii
                    note_lines[current_line] += note_lines.pop(current_line + 1)
                else:
                    note_lines[current_line] = (
                            note_lines[current_line][:cursor_x]
                            + note_lines[current_line][cursor_x + 1:]
                    )
        elif curses.keyname(key) == b'^S':  # save the note
            note.content = "\n".join(note_lines)
            update_note(note)

            # remove old message
            stdscr.addstr(curses.LINES - 1, 0, " " * len(title_str + shortcuts_str), curses.color_pair(1))
            # add new message
            stdscr.addstr(curses.LINES - 1, 0, "Saved!", curses.color_pair(2))

            stdscr.refresh()
            curses.napms(1000)

            ensure_decrypted_note(note)
        elif curses.keyname(key) == b'^E':
            return NavigationResult(NavigationAction.SUCCESS, None)
        else:
            # add new character
            # check if maximum width is reached
            if len(note_lines[current_line]) >= curses.COLS:
                continue
            note_lines[current_line] = (
                    note_lines[current_line][:cursor_x]
                    + chr(key)
                    + note_lines[current_line][cursor_x:]
            )
            cursor_x += 1
            is_modified = True


def handle_auth(stdscr):
    while True:
        user_choice = draw_main_login_screen(stdscr)

        if user_choice == AuthAction.LOGIN:
            while True:

                # try to log in last user, if not possible - show user select screen
                user = fetch_last_user()
                if user is not None:
                    if draw_pin_auth_screen(stdscr, user).action == NavigationAction.SUCCESS:
                        # user logged in successfully
                        return NavigationResult(NavigationAction.SUCCESS, user)

                    # user cancel auth by pressing 'q' - remove last user from db
                    clear_last_user()
                    continue

                select_result = draw_user_select_screen(stdscr, fetch_users())
                if select_result.action == NavigationAction.BACK:
                    break
                if select_result.data is None:
                    continue

                # user selected, show pin auth screen
                user = fetch_user_by_id(str(select_result.data))
                # print("Selected user: " + user.display_name)

                if draw_pin_auth_screen(stdscr, user).action == NavigationAction.SUCCESS:
                    return NavigationResult(NavigationAction.SUCCESS, user)

        elif user_choice == AuthAction.REGISTER:
            draw_register_screen(stdscr)
        elif user_choice == AuthAction.EXIT:
            exit(0)
        elif user_choice == AuthAction.ABOUT:
            display_program_info(stdscr)


def main(stdscr):
    init()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    stdscr.clear()

    while True:
        auth_result = handle_auth(stdscr)
        if auth_result.action == NavigationAction.FAILURE:
            return

        user = auth_result.data
        while True:
            notes_result = draw_notes_select_screen(stdscr, user)
            if notes_result.action == NavigationAction.EXIT:
                exit(0)
            elif notes_result.action == NavigationAction.BACK:
                break

            note = notes_result.data
            draw_note_edit_screen(stdscr, note)


curses.wrapper(main)
