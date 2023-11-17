from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

import database
import security

# secure that
user_key = None
user_iv = None


def create_user(name):
    Session = sessionmaker(bind=database.engine)
    session = Session()

    pin = input("Podaj pin: ")

    user = database.User(pin_hash=security.create_pin_hash(pin), display_name=name)

    try:
        while True:
            pin = input("Podaj pin ponownie: ")
            pin_hash = security.create_pin_hash(pin)
            if pin_hash == user.pin_hash:
                break
            else:
                print("Pin się nie zgadza, spróbuj ponownie.")
    except Exception as e:
        print("Wystąpił błąd: {}".format(e))
    finally:
        session.add(user)
        session.commit()
        print("Użytkownik został utworzony")

    return user, session  # Zwracamy również sesję


#    for user in users:
#        print(f"ID: {user.user_id}, Nazwa: {user.display_name}")
def fetch_users():
    Session = sessionmaker(bind=database.engine)
    session = Session()
    users = session.query(database.User.user_id, database.User.display_name).all()
    return users


def fetch_user_by_id(user_id):
    Session = sessionmaker(bind=database.engine)
    session = Session()

    user = session.query(database.User).filter(database.User.user_id == user_id).first()
    if user is None:
        print(f"Nie znaleziono użytkownika o id: {user_id}")
        return None
    return user


def fetch_last_user_id():
    Session = sessionmaker(bind=database.engine)
    session = Session()

    app_settings = session.query(database.AppSettings).first()
    if app_settings is None:
        return 0
    return app_settings.last_user_id


def uptate_last_application_user(user):
    Session = sessionmaker(bind=database.engine)
    session = Session()

    app_settings = session.query(database.AppSettings).first()
    if app_settings is None:
        app_settings = database.AppSettings()
        app_settings.last_user_id = user.user_id
        session.add(app_settings)
    else:
        app_settings.last_user_id = user.user_id

    session.commit()
    session.close()