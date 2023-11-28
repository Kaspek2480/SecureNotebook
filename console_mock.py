import database
import manager


def get_user():
    last_user_id = manager.fetch_last_user()
    if last_user_id != 0:
        user = manager.fetch_user_by_id(last_user_id)
        if user is not None:
            return user

    # last seen user not found, print all users
    users = manager.fetch_users()
    if len(users) == 0:
        print("Nie bazie nie ma żadnych użytkowników!")
        return None
    else:
        print("Użytkownicy platformy:")
        for user in users:
            print(f"Nazwa: {user.display_name} | id: {user.user_id}")
        user_id = input("Podaj ID użytkownika: ")

        user = manager.fetch_user_by_id(user_id)
        if user is None:
            return None
        else:
            return user


# def generate_notes():
#     notes = []
#     for i in range(10):
#         boxdel = manager.fetch_user_by_id(12)
#         if not boxdel.verify_pin("123"):
#             print("Pin się nie zgadza!")
#             exit(1)
#
#         note = database.Note(
#             title=f"Piękna notatka {i}",
#             content=f"To jest piękna notatka {i}",
#         )
#         boxdel.update_note(note)
#     return notes


if __name__ == '__main__':
    database.init()
    generate_notes()

    # user = get_user()
    # if user is None:
    #     print("Tworzysz nowego użytkownika")
    #     print("Podaj imię: ")
    #
    #     user, session = manager.create_user(input())
    #
    # print(f"Witaj {user.display_name}!")
    # pin = input("Podaj pin: ")
    # if not user.verify_pin(pin):
    #     print("Pin się nie zgadza!")
    #     exit(1)
    #
    # print("Witaj w aplikacji!")
    #
    # notes = user.notes
    # print("Twoje notatki:")
    # for note in notes:
    #     print(f"ID: {note.note_id} | Tytuł: {note.title}")
    #
    # # note = database.Note(title="Piękna notatka", content="To jest piękna notatka")
    # # user.update_note(note)
    #
    # first_note = notes[0]
    # first_note.title = first_note.title + "1"
    #
    # user.update_note(first_note)
