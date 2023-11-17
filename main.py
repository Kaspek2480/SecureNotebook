import database
import manager

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Stworzenie nowej sesji
    database.create_table()

    # name = input("Podaj imię: ")
    # manager.create_user(name)
    users = manager.fetch_user_by_id(user_id=2)
    if users is None:
        print("Nie znaleziono użytkownika")
    else:
        print("Znaleziono użytkownika")
        print(users.display_name)
