import time
from datetime import datetime

from sqlalchemy import create_engine, event, orm
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, column_property

import manager
import security

# inicjalizacja połaczenia z bazą danych
engine = create_engine('sqlite:///notebook_database.sqlite', echo=False)
conn = engine.connect()

Base = declarative_base()


class Tag(Base):
    __tablename__ = 'tag'

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    def __init__(self, name):
        super().__init__()
        self.name = name


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String)
    pin_hash = Column(String)
    last_note_id = Column(Integer)

    created_timestamp = Column(Integer)
    last_access_timestamp = Column(Integer)

    notes = []

    def __init__(self, pin_hash, display_name):
        super().__init__()
        self.pin_hash = pin_hash
        self.display_name = display_name
        self.last_note_id = 0
        self.created_timestamp = int(datetime.now().timestamp())
        self.last_access_timestamp = int(datetime.now().timestamp())

    @orm.reconstructor
    def init_on_load(self):
        print("Executed user init_on_load with " + self.display_name)

    def verify_pin(self, pin):
        if self.pin_hash != security.create_pin_hash(pin):
            return False

        self.init_after_auth(pin)
        return True

    def init_after_auth(self, pin):
        key_pair = security.calculate_key(pin)
        manager.user_key = key_pair['key']
        manager.user_iv = key_pair['iv']

        manager.uptate_last_application_user(self)

        self.update_last_access()
        self.fetch_user_notes()

    def fetch_user_notes(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        # notes = session.query(Note).join(UserNoteLink).filter(UserNoteLink.user_id == self.user_id).all()

        # users = session.query(database.User.user_id, database.User.display_name).all()
        for note in session.query(Note).all():
            session.expunge(note)
            note.ensure_decrypted()
            self.notes.append(note)
        session.close()

        return self.notes

    def update_note(self, note):
        if note is None:
            raise Exception("update_note: not is None")

        note.ensure_encrypted()

        # check if note exists
        Session = sessionmaker(bind=engine)
        session = Session()
        note_result = session.query(Note).filter(Note.note_id == note.note_id).first()
        session.close()

        # create new note if not exists
        if note_result is None:

            Session = sessionmaker(bind=engine)
            session = Session()
            session.add(note)
            session.commit()

            UserNoteLink.create_user_note_link(session, self, note)

            session.close()
            return

        # update note
        note.update_last_modify()

    def update_last_access(self):
        self.last_access_timestamp = int(datetime.now().timestamp())
        self.update_itself()

    def update_itself(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        session.close()


class Note(Base):
    __tablename__ = 'note'

    note_id = Column(Integer, primary_key=True, autoincrement=True)
    priority = Column(Integer)
    title = Column(String)
    content = Column(String)
    created_timestamp = Column(Integer)
    last_modify_timestamp = Column(Integer)

    encrypted = True

    # invoked only when creating new note
    def __init__(self, title, content):
        print("Executed __init__ with " + content)
        super().__init__()

        self.encrypted = False
        self.title = title
        self.content = content
        self.priority = 0
        self.created_timestamp = int(time.time())
        self.last_modify_timestamp = int(time.time())

    # invoked while fetching from db
    @orm.reconstructor
    def init_on_load(self):
        print("Executed note init_on_load with " + self.content)
        self.encrypted = True

    def update_itself(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        session.close()

    def update_last_modify(self):
        self.last_modify_timestamp = int(datetime.now().timestamp())
        self.update_itself()

    def decrypt(self):
        if self.encrypted:
            self.content = security.decrypt_text(manager.user_key, manager.user_iv, bytes.fromhex(self.content))
            self.title = security.decrypt_text(manager.user_key, manager.user_iv, bytes.fromhex(self.title))
            self.encrypted = False

    def encrypt(self):
        if not self.encrypted:
            self.content = security.encrypt_text(manager.user_key, manager.user_iv, self.content.encode())
            self.title = security.encrypt_text(manager.user_key, manager.user_iv, self.title.encode())
            self.encrypted = True

    def ensure_encrypted(self):
        if not self.encrypted:
            self.encrypt()

    def ensure_decrypted(self):
        if self.encrypted:
            self.decrypt()


class UserNoteLink(Base):
    __tablename__ = 'user_note_link'

    user_id = Column(Integer, primary_key=True)
    note_id = Column(Integer, primary_key=True)

    def __init__(self, user_id, note_id):
        super().__init__()
        self.user_id = user_id
        self.note_id = note_id

    @staticmethod
    def create_user_note_link(session, user, note):
        user_note_link = UserNoteLink(user_id=user.user_id, note_id=note.note_id)
        session.add(user_note_link)
        session.commit()
        session.close()

    @staticmethod
    def delete_user_note_link(user, note):
        Session = sessionmaker(bind=engine)
        session = Session()

        user_note_link = session.query(UserNoteLink).filter(UserNoteLink.user_id == user.user_id,
                                                            UserNoteLink.note_id == note.note_id).first()
        session.delete(user_note_link)
        session.commit()
        session.close()


class AppSettings(Base):
    __tablename__ = 'app_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_user_id = Column(Integer)
    last_note_id = Column(Integer)

    def __init__(self):
        super().__init__()
        self.last_user_id = 0
        self.last_note_id = 0


def create_table():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_table()
