import sys
from os.path import abspath, dirname
from tkinter import messagebox

# Add the 'shared' directory to the Python path
sys.path.append(abspath(dirname(dirname(__file__))))

import os
import tkinter

import customtkinter
from PIL import Image

from shared.database import init
from shared.manager import *
from gui.gui_utils import *

input_pin = None
initialized = False


class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, item, image=None):
        label = customtkinter.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(self, text="Zaloguj", width=60, height=24, border_color="gray70",
                                         border_width=1, fg_color="transparent", text_color=("gray10", "gray90"),
                                         hover_color=("gray70", "gray30"))
        if self.command is not None:
            button.configure(command=lambda: self.command(item))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return


class UserList(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, item, image=None):
        item_id = item["id"]
        item_name = item["name"]

        def cmd():
            print(f"login button clicked: {item_id}")
            if initialized:
                print("initialized")

        label = customtkinter.CTkLabel(self, text=item_name, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(self, text="Zaloguj", width=60, height=24, border_color="gray70",
                                         border_width=1, fg_color="transparent", text_color=("gray10", "gray90"),
                                         hover_color=("gray70", "gray30"), command=cmd())

        label.grid(row=len(self.label_list), column=0, pady=(10, 20), sticky="w")  # Increased padding for each item
        button.grid(row=len(self.button_list), column=1, pady=(10, 20), padx=5)  # Increased padding for each item
        self.label_list.append(label)
        self.button_list.append(button)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.user_pin = None
        self.iconbitmap("resources/app_icon.ico")

        self.title("Secure Notebook - Twoje bezpieczne notatki")
        self.geometry("1000x600")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # <editor-fold desc="load images">
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
        self.logo_image = customtkinter.CTkImage(dark_image=Image.open(os.path.join(image_path, "app_icon.png")),
                                                 size=(26, 26))
        self.login_image = customtkinter.CTkImage(dark_image=Image.open(os.path.join(image_path, "login/login.png")),
                                                  size=(20, 20))
        self.register_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(image_path, "login/sign_in.png")), size=(20, 20))
        self.about_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(image_path, "login/icons8-help-48.png")), size=(20, 20))
        self.exit_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(image_path, "login/icons8-exit-48.png")), size=(20, 20))
        self.user_image = customtkinter.CTkImage(
            dark_image=Image.open(os.path.join(image_path, "login/icons8-user-menu-male-96.png")), size=(20, 20))
        # </editor-fold>

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.login_frame = self.create_login_frame()

        self.register_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.register_frame.grid_columnconfigure(0, weight=1)

        self.about_frame = self.create_about_frame()

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=" Secure Notebook",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # <editor-fold desc="navigation buttons">
        self.login_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                    border_spacing=10, text="Logowanie",
                                                    fg_color="transparent", text_color=("gray10", "gray90"),
                                                    hover_color=("gray70", "gray30"),
                                                    image=self.login_image, anchor="w", command=self.login_button_event)
        self.login_button.grid(row=1, column=0, sticky="ew")

        self.register_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Rejestracja",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.register_image, anchor="w",
                                                       command=self.register_button_event)
        self.register_button.grid(row=2, column=0, sticky="ew")

        self.about_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                    border_spacing=10, text="O programie",
                                                    fg_color="transparent", text_color=("gray10", "gray90"),
                                                    hover_color=("gray70", "gray30"),
                                                    image=self.about_image, anchor="w", command=self.about_button_event)
        self.about_button.grid(row=3, column=0, sticky="ew")

        self.exit_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Wyjdź",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.exit_image, anchor="w", command=self.exit_button_event)
        self.exit_button.grid(row=4, column=0, sticky="ew")
        # </editor-fold>

        # Label for displaying login status
        self.login_status_label = customtkinter.CTkLabel(self.navigation_frame, text="Not Logged In",
                                                         fg_color="transparent",
                                                         text_color=("gray10", "gray90"),
                                                         font=customtkinter.CTkFont(size=12))
        self.login_status_label.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        global initialized
        initialized = True
        self.select_frame_by_name("login")

    def create_about_frame(self) -> customtkinter.CTkFrame:
        about_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        about_frame.grid_columnconfigure(0, weight=1)
        about_frame.grid_rowconfigure(0, pad=60)  # increasing top padding

        main_label_font = customtkinter.CTkFont(family="Helvetica", size=23, weight="bold")  # enlarging main text font
        main_info_label = customtkinter.CTkLabel(about_frame,
                                                 text="Witaj w SecureNotebook - bezpiecznym miejscu na Twoje notatki!",
                                                 font=main_label_font, width=120, height=25)
        main_info_label.grid(row=0, column=0, padx=20, pady=20)

        detailed_info = "Twoje notatki są zabezpieczone przed nieautoryzowanym dostępem.\n " \
                        "Wykorzystujemy mocne szyfrowanie AES-256-CBC do ochrony treści.\n " \
                        "Klucz do odszyfrowania jest generowany z PIN-u z użyciem KDF PBKDF2.\n " \
                        "Ta technika jest znana z menedżerów haseł, co oznacza, że jesteś w dobrych rękach.\n"

        detailed_info_font = customtkinter.CTkFont(family="Arial", size=16)  # enlarging details font
        detailed_info_label = customtkinter.CTkLabel(about_frame, text=detailed_info, width=120, height=25,
                                                     font=detailed_info_font)
        detailed_info_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        detailed_info_label.grid(row=1, column=0, padx=20, pady=20)

        detailed_info_2 = (
            "KDF jest potrzebny aby zapewnić bezpieczeństwo notatkom, ponieważ wprowadza element trudności w atakach brute force, gdzie potencjalny atakujący próbuje odgadnąć hasło poprzez wypróbowanie wszystkich możliwych kombinacji. "
            "Dzięki funkcji kluczowego pochodzenia proces ten staje się bardziej złożony, nawet gdy pierwotne hasło jest dość proste. "
            "Dodatkowo, KDF pomaga w zabezpieczeniu przed atakami typu \"rainbow table\", gdzie atakujący korzysta z gotowych zestawów zahaszowanych haseł w celu przyspieszenia ataku.")
        detailed_info_2_label = customtkinter.CTkLabel(about_frame, text=detailed_info_2, width=120, height=25,
                                                       font=detailed_info_font, wraplength=600)
        detailed_info_2_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        return about_frame

    def create_login_frame(self) -> customtkinter.CTkFrame:
        login_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_rowconfigure(0, pad=60)  # increasing top padding

        main_label_font = customtkinter.CTkFont(family="Helvetica", size=20)  # enlarging main text font
        main_info_label = customtkinter.CTkLabel(login_frame,
                                                 text="Wybierz użytkownika, aby się zalogować:",
                                                 font=main_label_font, width=120, height=25)
        main_info_label.grid(row=0, column=0, padx=20, pady=20)

        user_list = UserList(master=login_frame, width=700, height=400,
                             corner_radius=0)
        user_list.place(relx=0.5, rely=0.5, anchor='center')

        users = fetch_users()
        for user in users:
            user_list.add_item({"id": user.user_id, "name": user.display_name}, image=self.user_image)

        return login_frame

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.login_button.configure(fg_color=("gray75", "gray25") if name == "login" else "transparent")
        self.register_button.configure(fg_color=("gray75", "gray25") if name == "register" else "transparent")
        self.about_button.configure(fg_color=("gray75", "gray25") if name == "about" else "transparent")

        # show selected frame
        if name == "login":
            self.login_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.login_frame.grid_forget()
        if name == "register":
            self.register_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.register_frame.grid_forget()
        if name == "about":
            self.about_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.about_frame.grid_forget()

    def login_button_event(self):
        self.select_frame_by_name("login")

    def register_button_event(self):
        self.select_frame_by_name("register")

    def about_button_event(self):
        self.select_frame_by_name("about")

    def exit_button_event(self):
        self.destroy()


if __name__ == "__main__":
    init()

    app = App()
    app.mainloop()
