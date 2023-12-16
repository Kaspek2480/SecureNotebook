from sqlalchemy.orm import sessionmaker
import security
import database

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

    notes_id_list = session.query(database.UserNoteLink.note_id).filter(database.UserNoteLink.user_id == user_id).all()

    if not notes_id_list:
        session.close()
        return note_list

    # Rozpakuj tuplę z listy ID notatek
    notes_id_list = [note_id[0] for note_id in notes_id_list]

    for note_id in notes_id_list:
        note = session.query(database.Note).filter(database.Note.note_id == note_id).first()
        if note:
            session.expunge(note)
            note.ensure_decrypted()
            note_list.append(note)

    session.close()

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


def update_note(note):
    note.ensure_encrypted()
    note.update_last_modify()

    Session = sessionmaker(bind=database.engine)
    session = Session()

    session.merge(note)
    session.commit()
    session.close()
