import os
import tkinter
from tkinter import Scrollbar, Listbox

import customtkinter
from PIL import Image

from CTkTable import *
from shared.database import init
from shared.manager import *
from gui.gui_utils import *


class NoteList(customtkinter.CTkScrollableFrame):
    def __init__(self, master, fav_command, edit_command, delete_command, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        if fav_command is None or edit_command is None or delete_command is None:
            raise Exception("NoteList: fav_command, edit_command and delete_command must be not None")

        self.star_command = fav_command
        self.edit_command = edit_command
        self.delete_command = delete_command

        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, note_obj, image=None):
        # note_id=1, title="Test"
        note_id = note_obj.note_id
        title = note_obj.title
        is_favorite = note_obj.favorite

        label = customtkinter.CTkLabel(self, text="  " + title, image=image, compound="left", padx=5, pady=5,
                                       anchor="w")
        label.grid(row=len(self.label_list), column=0, pady=(10, 20), sticky="w")  # Increased padding for each item

        star_note_button = customtkinter.CTkButton(self, text="", width=15, height=24, border_color="gray70",
                                                   border_width=1, fg_color="transparent",
                                                   image=dashboard_star_filled_note_icon if is_favorite else dashboard_star_note_icon,
                                                   text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   command=lambda: self.star_command(note_obj))
        delete_note_button = customtkinter.CTkButton(self, text="", width=15, height=24, border_color="gray70",
                                                     border_width=1, fg_color="transparent",
                                                     text_color=("gray10", "gray90"),
                                                     hover_color=("gray70", "gray30"), image=dashboard_delete_note_icon,
                                                     command=lambda: self.delete_command(note_obj))
        edit_note_button = customtkinter.CTkButton(self, text="", width=15, height=24, border_color="gray70",
                                                   border_width=1, fg_color="transparent",
                                                   image=dashboard_edit_note_icon,
                                                   text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   command=lambda: self.edit_command(note_obj))

        # edit_note_button.grid(row=len(self.button_list), column=2, pady=(10, 20), padx=2)
        # star_note_button.grid(row=len(self.button_list), column=1, pady=(10, 20), padx=2)
        # delete_note_button.grid(row=len(self.button_list), column=3, pady=(10, 20), padx=2)

        edit_note_button.grid(row=len(self.button_list), column=2, pady=(10, 20), padx=2)
        star_note_button.grid(row=len(self.button_list), column=1, pady=(10, 20), padx=2)
        delete_note_button.grid(row=len(self.button_list), column=3, pady=(10, 20), padx=2)

        self.label_list.append(label)
        self.button_list.append(star_note_button)
        # self.button_list.append(delete_note_button)
        # self.button_list.append(edit_note_button)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return

    def clear(self):
        for label, button in zip(self.label_list, self.button_list):
            label.destroy()
            button.destroy()
        self.label_list.clear()
        self.button_list.clear()


class Dashboard(customtkinter.CTk):
    def __init__(self, user, root):
        super().__init__()

        self.user_obj = user
        self.root = root

        self.note_list = None
        self.iconbitmap("resources/icons8-secure-100.ico")

        self.title("Secure Notebook - Twoje bezpieczne notatki")
        self.geometry("900x600")
        self.resizable(False, False)

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # <editor-fold desc="load images">
        self.logo_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(resource_path, "icons8-secure-100.png")),
            size=(26, 26))
        self.login_image = customtkinter.CTkImage(dark_image=Image.open(os.path.join(resource_path, "login/login.png")),
                                                  size=(20, 20))
        self.add_note_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-add-96.png")),
            size=(20, 20))
        self.home_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-home-page-96.png")), size=(20, 20))
        self.user_profile_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-tools-96.png")), size=(20, 20))
        self.logout_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-logout-96.png")), size=(20, 20))
        self.user_logo_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-user-100.png")), size=(20, 20))
        # </editor-fold>

        # <editor-fold desc="navigation frame">
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Secure Notebook",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"),
                                                             padx=10, pady=10)
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        # </editor-fold>

        # <editor-fold desc="navigation buttons">
        self.add_note_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Nowa",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.add_note_image, anchor="w",
                                                       command=lambda: self.switch_frame("add_note"))
        self.add_note_button.grid(row=1, column=0, sticky="ew")

        self.user_notes_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                         border_spacing=10, text="Notatki",
                                                         fg_color="transparent", text_color=("gray10", "gray90"),
                                                         hover_color=("gray70", "gray30"),
                                                         image=self.home_image, anchor="w",
                                                         command=lambda: self.switch_frame("user_notes"))
        self.user_notes_button.grid(row=2, column=0, sticky="ew")

        self.user_profile_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                           border_spacing=10, text="Profil",
                                                           fg_color="transparent", text_color=("gray10", "gray90"),
                                                           hover_color=("gray70", "gray30"),
                                                           image=self.user_profile_image, anchor="w",
                                                           command=lambda: self.switch_frame("user_profile"))
        self.user_profile_button.grid(row=3, column=0, sticky="ew")

        self.logout_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                     border_spacing=10, text="Wyloguj",
                                                     fg_color="transparent", text_color=("gray10", "gray90"),
                                                     hover_color=("gray70", "gray30"),
                                                     image=self.logout_image, anchor="w",
                                                     command=lambda: self.switch_frame("logout"))
        self.logout_button.grid(row=4, column=0, sticky="ew")
        # </editor-fold>

        self.home_frame = self.create_user_notes_frame()
        self.add_note_frame = self.create_add_note_frame()
        self.user_profile_frame = self.create_user_profile_frame()
        self.logout_frame = self.create_logout_frame()

        self.user_navbar_label = customtkinter.CTkLabel(self.navigation_frame, text=f"   {user.display_name}",
                                                        image=self.user_logo_image,
                                                        compound="left",
                                                        font=customtkinter.CTkFont(size=12),
                                                        padx=5, pady=5, height=20, fg_color="transparent", anchor="w")
        self.user_navbar_label.grid(row=6, column=0, padx=10, pady=10)

        self.switch_frame("user_notes")

    def create_user_notes_frame(self) -> customtkinter.CTkFrame:
        user_notes_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        user_notes_frame.grid_columnconfigure(0, weight=1)

        def star_impl(note):
            change_note_favorite(note, not note.favorite)
            self.reload_notes()

        def edit_impl(note):
            print("edit_impl")

        def delete_impl(note):
            print("delete_impl")

        self.note_list = NoteList(master=user_notes_frame, width=600, height=400, corner_radius=0,
                                  fav_command=star_impl, edit_command=edit_impl, delete_command=delete_impl)
        self.note_list.place(relx=0.5, rely=0.5, anchor='center')

        # note = Note(title="Test", content="Test")
        # self.note_list.add_item(note)

        return user_notes_frame

    def create_add_note_frame(self) -> customtkinter.CTkFrame:
        add_note_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        add_note_frame.grid_columnconfigure(0, weight=1)

        add_note_frame_label = customtkinter.CTkLabel(add_note_frame, text="Dodaj nową notatkę",
                                                      font=customtkinter.CTkFont(size=20, weight="bold"))
        add_note_frame_label.grid(row=0, column=0, padx=30, pady=(30, 15))
        add_note_frame_button = customtkinter.CTkButton(add_note_frame, text="Dodaj", width=200)
        add_note_frame_button.grid(row=1, column=0, padx=30, pady=(15, 15))

        return add_note_frame

    def create_user_profile_frame(self) -> customtkinter.CTkFrame:
        user_profile_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        user_profile_frame.grid_columnconfigure(0, weight=1)

        user_profile_frame_label = customtkinter.CTkLabel(user_profile_frame, text="Profil użytkownika",
                                                          font=customtkinter.CTkFont(size=20, weight="bold"))
        user_profile_frame_label.grid(row=0, column=0, padx=30, pady=(30, 15))
        user_profile_frame_button = customtkinter.CTkButton(user_profile_frame, text="Zmień hasło", width=200)
        user_profile_frame_button.grid(row=1, column=0, padx=30, pady=(15, 15))

        return user_profile_frame

    def create_logout_frame(self) -> customtkinter.CTkFrame:
        logout_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        logout_frame.grid_columnconfigure(0, weight=1)

        logout_frame_label = customtkinter.CTkLabel(logout_frame, text="Wylogowanie",
                                                    font=customtkinter.CTkFont(size=20, weight="bold"))
        logout_frame_label.grid(row=0, column=0, padx=30, pady=(30, 15))
        logout_frame_button = customtkinter.CTkButton(logout_frame, text="Wyloguj", width=200)
        logout_frame_button.grid(row=1, column=0, padx=30, pady=(15, 15))

        return logout_frame

    def reload_notes(self):
        self.note_list.clear()

        for note in fetch_user_notes(self.user_obj.user_id):
            ensure_decrypted_note(note)
            self.note_list.add_item(note)

    def switch_frame(self, name: str):
        # set button color for selected button
        self.add_note_button.configure(fg_color=("gray75", "gray25") if name == "add_note" else "transparent")
        self.user_notes_button.configure(fg_color=("gray75", "gray25") if name == "user_notes" else "transparent")
        self.user_profile_button.configure(fg_color=("gray75", "gray25") if name == "user_profile" else "transparent")

        # show selected frame
        if name == "add_note":
            self.add_note_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.add_note_frame.grid_forget()

        if name == "user_notes":
            self.reload_notes()
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()

        if name == "user_profile":
            self.user_profile_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.user_profile_frame.grid_forget()

        if name == "logout":
            self.logout_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.logout_frame.grid_forget()


if __name__ == "__main__":
    user = fetch_user_by_id(12)
    initialize_user(user, "123")
    app = Dashboard(user, None)
    app.mainloop()
