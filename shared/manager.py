import threading

from sqlalchemy.orm import sessionmaker

from shared.database import User, engine, Note, AppSettings, UserNoteLink
from shared.security import create_pin_hash, calculate_key, decrypt_text, encrypt_text

# secure that
user_key = None
user_iv = None


def create_user(name, pin):
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(pin_hash=create_pin_hash(pin), display_name=name)

    session.add(user)
    session.commit()

    return True


#    for user in users:
#        print(f"ID: {user.user_id}, Nazwa: {user.display_name}")
def fetch_users():
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(User.user_id, User.display_name, User.last_access_timestamp).all()
    return users


def fetch_user_by_id(user_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.user_id == user_id).first()
    if user is None:
        return None

    session.expunge(user)
    session.close()

    return user


def fetch_last_user():
    Session = sessionmaker(bind=engine)
    session = Session()

    app_settings = session.query(AppSettings).first()
    if app_settings is None:
        return None

    user = fetch_user_by_id(app_settings.last_user_id)
    if user is None:
        return None

    return user


def fetch_user_notes(user_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    note_list = []

    notes_id_list = session.query(UserNoteLink.note_id).filter(UserNoteLink.user_id == user_id).all()

    if not notes_id_list:
        session.close()
        return note_list

    # Rozpakuj tuplę z listy ID notatek
    notes_id_list = [note_id[0] for note_id in notes_id_list]

    for note_id in notes_id_list:
        note = session.query(Note).filter(Note.note_id == note_id).first()
        if note:
            session.expunge(note)
            ensure_decrypted_note(note)
            note_list.append(note)

    session.close()

    note_list.sort(key=lambda x: x.favorite, reverse=True)

    return note_list


def uptate_last_application_user(user):
    Session = sessionmaker(bind=engine)
    session = Session()

    app_settings = session.query(AppSettings).first()
    if app_settings is None:
        app_settings = AppSettings()
        app_settings.last_user_id = user.user_id
        session.add(app_settings)
    else:
        app_settings.last_user_id = user.user_id

    session.commit()
    session.close()


def clear_last_user():
    Session = sessionmaker(bind=engine)
    session = Session()

    app_settings = session.query(AppSettings).first()
    if app_settings is None:
        return None

    app_settings.last_user_id = 0
    session.commit()
    session.close()


def update_note(note):
    ensure_encrypted_note(note)
    note.update_last_modify()

    Session = sessionmaker(bind=engine)
    session = Session()

    session.merge(note)
    session.commit()
    session.close()


def verify_user_pin(user, pin):
    return user.pin_hash == create_pin_hash(pin)


def initialize_user(user, pin):
    global user_key
    global user_iv

    key_pair = calculate_key(pin)
    user_key = key_pair['key']
    user_iv = key_pair['iv']

    # update everything in the background
    threading.Thread(target=uptate_last_application_user(user)).start()
    threading.Thread(target=user.update_last_access()).start()

    user.notes = fetch_user_notes(user.user_id)


def ensure_decrypted_note(note):
    if note.encrypted:
        note.content = decrypt_text(user_key, user_iv, bytes.fromhex(note.content))
        note.title = decrypt_text(user_key, user_iv, bytes.fromhex(note.title))
        note.encrypted = False


def ensure_encrypted_note(note):
    if not note.encrypted:
        note.content = encrypt_text(user_key, user_iv, note.content.encode())
        note.title = encrypt_text(user_key, user_iv, note.title.encode())
        note.encrypted = True
