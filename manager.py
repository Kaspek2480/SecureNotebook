from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

import database
import security

# secure that
user_key = None
user_iv = None


def create_user(name, pin):
    Session = sessionmaker(bind=database.engine)
    session = Session()

    user = database.User(pin_hash=security.create_pin_hash(pin), display_name=name)

    session.add(user)
    session.commit()

    return True


#    for user in users:
#        print(f"ID: {user.user_id}, Nazwa: {user.display_name}")
def fetch_users():
    Session = sessionmaker(bind=database.engine)
    session = Session()
    users = session.query(database.User.user_id, database.User.display_name, database.User.last_access_timestamp).all()
    return users


def fetch_user_by_id(user_id):
    Session = sessionmaker(bind=database.engine)
    session = Session()

    user = session.query(database.User).filter(database.User.user_id == user_id).first()
    if user is None:
        return None

    session.expunge(user)
    session.close()

    return user


def fetch_last_user():
    Session = sessionmaker(bind=database.engine)
    session = Session()

    app_settings = session.query(database.AppSettings).first()
    if app_settings is None:
        return None

    user = fetch_user_by_id(app_settings.last_user_id)
    if user is None:
        return None

    return user


def fetch_user_notes(user_id):
    Session = sessionmaker(bind=database.engine)
    session = Session()

    note_list = []
    notes = session.query(database.Note).filter(database.UserNoteLink.user_id == user_id).all()

    for note in notes:
        session.expunge(note)
        note.ensure_decrypted()
        note_list.append(note)
    session.close()

    # sort by favorite
    note_list.sort(key=lambda x: x.favorite, reverse=True)

    return note_list


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


def clear_last_user():
    Session = sessionmaker(bind=database.engine)
    session = Session()

    app_settings = session.query(database.AppSettings).first()
    if app_settings is None:
        return None

    app_settings.last_user_id = 0
    session.commit()
    session.close()