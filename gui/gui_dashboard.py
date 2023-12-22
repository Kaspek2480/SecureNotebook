import os
import tkinter
from tkinter import Scrollbar, Listbox

import customtkinter
from PIL import Image

from CTkTable import *

from gui.gui_note_edit_view import NoteEditor
# from gui.gui_login_view import App
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

        self.label_count = 0
        self.button_count = 0

        self.add_labels()

    def add_labels(self):
        label = customtkinter.CTkLabel(self, text="  Tytuł", padx=5, pady=5, anchor="w")
        label2 = customtkinter.CTkLabel(self, text="Ostatnia edycja", padx=5, pady=5, anchor="w")
        empty_separator = customtkinter.CTkLabel(self, text="", padx=5, pady=5, anchor="w")

        label.grid(row=0, column=0, pady=(10, 10), sticky="w")
        label2.grid(row=0, column=1, pady=(10, 10), sticky="w")
        empty_separator.grid(row=0, column=2, pady=(10, 10), sticky="w")

        self.label_count += 1
        self.button_count += 1

    def add_item(self, note_obj, image=None):
        # note_id=1, title="Test"
        note_id = note_obj.note_id
        title = note_obj.title
        is_favorite = note_obj.favorite
        last_modify_timestamp = note_obj.last_modify_timestamp

        label = customtkinter.CTkLabel(self, text="  " + title, image=image, compound="left", padx=5, pady=5,
                                       anchor="w")
        label2 = customtkinter.CTkLabel(self, text=timestamp_to_date(last_modify_timestamp), image=image,
                                        compound="left", padx=5, pady=5, anchor="w")
        empty_separator = customtkinter.CTkLabel(self, text="", padx=5, pady=5, anchor="w")
        empty_separator2 = customtkinter.CTkLabel(self, text="", padx=2, pady=2, anchor="w")

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

        label.grid(row=self.label_count, column=0, pady=(10, 10), sticky="w")  # Increased padding for each item
        label2.grid(row=self.label_count, column=1, pady=(10, 20), sticky="w")
        empty_separator.grid(row=self.label_count, column=2, pady=(10, 20), sticky="w")

        star_note_button.grid(row=self.button_count, column=3, pady=(10, 20), padx=2)
        edit_note_button.grid(row=self.button_count, column=4, pady=(10, 20), padx=2)
        delete_note_button.grid(row=self.button_count, column=5, pady=(10, 20), padx=2)
        empty_separator2.grid(row=self.button_count, column=6, pady=(10, 20), sticky="w")

        self.label_count += 1
        self.button_count += 1

    # def remove_item(self, item):
    #     for label, button in zip(self.label_list, self.button_list):
    #         if item == label.cget("text"):
    #             label.destroy()
    #             button.destroy()
    #             self.label_list.remove(label)
    #             self.button_list.remove(button)
    #             return

    def clear(self):
        print("Create new list")


class Dashboard:
    def __init__(self, user, root, exit_callback=None):
        super().__init__()

        self.user_notes_frame = None
        self.user_obj = user
        self.root = root
        self.logout_callback = exit_callback

        self.note_list = None
        # root.iconbitmap("resources/icons8-secure-100.ico")

        # root.title("Secure Notebook - Twoje bezpieczne notatki")
        # root.geometry("900x600")
        # root.resizable(False, False)

        # set grid layout 1x2
        # root.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)

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
        self.navigation_frame = customtkinter.CTkFrame(self.root, corner_radius=0)
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
                                                       command=self.new_note_impl)
        self.add_note_button.grid(row=1, column=0, sticky="ew")

        self.user_notes_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                         border_spacing=10, text="Notatki",
                                                         fg_color="transparent", text_color=("gray10", "gray90"),
                                                         hover_color=("gray70", "gray30"),
                                                         image=self.home_image, anchor="w",
                                                         command=lambda: self.switch_frame("user_notes"))
        self.user_notes_button.grid(row=2, column=0, sticky="ew")

        # self.user_profile_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
        #                                                    border_spacing=10, text="Profil",
        #                                                    fg_color="transparent", text_color=("gray10", "gray90"),
        #                                                    hover_color=("gray70", "gray30"),
        #                                                    image=self.user_profile_image, anchor="w",
        #                                                    command=lambda: self.switch_frame("user_profile"))
        # self.user_profile_button.grid(row=3, column=0, sticky="ew")

        self.logout_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                     border_spacing=10, text="Wyloguj",
                                                     fg_color="transparent", text_color=("gray10", "gray90"),
                                                     hover_color=("gray70", "gray30"),
                                                     image=self.logout_image, anchor="w",
                                                     command=self.logout_impl)
        self.logout_button.grid(row=4, column=0, sticky="ew")
        # </editor-fold>

        self.home_frame = self.create_note_list_frame()

        self.user_navbar_label = customtkinter.CTkLabel(self.navigation_frame, text=f"   {user.display_name}",
                                                        image=self.user_logo_image,
                                                        compound="left",
                                                        font=customtkinter.CTkFont(size=12),
                                                        padx=5, pady=5, height=20, fg_color="transparent", anchor="w")
        self.user_navbar_label.grid(row=6, column=0, padx=10, pady=10)

        self.switch_frame("user_notes")

    def create_note_list_frame(self) -> customtkinter.CTkFrame:
        self.user_notes_frame = customtkinter.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.user_notes_frame.grid_columnconfigure(0, weight=1)
        self.user_notes_frame.grid_rowconfigure(0, pad=60)  # increasing top padding

        main_info_label = customtkinter.CTkLabel(self.user_notes_frame,
                                                 text="Twoje notatki:",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        main_info_label.grid(row=0, column=0, padx=20, pady=20)

        return self.user_notes_frame

    def star_impl(self, note):
        change_note_favorite(note, not note.favorite)
        self.reload_notes()

    def edit_impl(self, note):
        def exit_callback():
            print("Editor closed")
            self.reload_notes()

        editor = NoteEditor(note, exit_callback, self.root)
        editor.grab_set()
        editor.after(100, editor.lift)  # Workaround for bug where main window takes focus
        editor.after(100, editor.focus_force)  # Workaround for bug where main window takes focus
        editor.after(100, editor.textbox.focus)  # Workaround for bug where main window takes focus

    def delete_impl(self, note):
        # ask user if he is sure
        if not messagebox.askyesno("Usuwanie notatki", "Czy na pewno chcesz usunąć tą notatkę?"):
            return

        self.user_obj.remove_note(note)
        self.reload_notes()

    def new_note_impl(self):
        # set button color for selected button
        self.user_notes_button.configure(fg_color="transparent")
        self.add_note_button.configure(fg_color=("gray75", "gray25"))

        user_input = get_user_input("Dodawanie notatki", "Podaj tytuł notatki")
        if user_input is not None and len(user_input) > 0:
            created_note = Note(title=user_input)
            ensure_encrypted_note(created_note)

            self.user_obj.update_note(created_note)
            self.reload_notes()

        # set color back to default
        self.add_note_button.configure(fg_color="transparent")
        self.user_notes_button.configure(fg_color=("gray75", "gray25"))

    def logout_impl(self):
        self.navigation_frame.destroy()
        self.user_notes_frame.destroy()
        self.user_navbar_label.destroy()

        if self.logout_callback is not None:
            self.logout_callback()

    def reload_notes(self):

        self.note_list = NoteList(master=self.user_notes_frame, width=600, height=400, corner_radius=0,
                                  fav_command=self.star_impl, edit_command=self.edit_impl,
                                  delete_command=self.delete_impl)
        self.note_list.place(relx=0.5, rely=0.5, anchor='center')

        for note in fetch_user_notes(self.user_obj.user_id):
            ensure_decrypted_note(note)
            self.note_list.add_item(note)

    def switch_frame(self, name: str):
        # set button color for selected button
        self.user_notes_button.configure(fg_color=("gray75", "gray25"))

        # show selected frame
        if name == "add_note":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
            self.new_note_impl()
            self.switch_frame("user_notes")

        if name == "user_notes":
            self.reload_notes()
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()


if __name__ == "__main__":
    user = fetch_user_by_id(12)
    initialize_user(user, "123")
    app = Dashboard(user, None)
    app.mainloop()
