import os
from datetime import datetime

from PIL import Image
from tkinter import messagebox

import customtkinter

resource_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
logo_image_path = os.path.join(resource_path, "icons8-secure-100.ico")
dashboard_delete_note_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-remove-100.png")), size=(15, 15))
dashboard_edit_note_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-edit-100.png")), size=(15, 15))
dashboard_star_note_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-star-100.png")), size=(15, 15))
dashboard_star_filled_note_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-filled-star-100.png")), size=(15, 15))
dashboard_save_file_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-save-100.png")), size=(20, 20))
dashboard_rollback_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-rollback-100.png")), size=(20, 20))
exit_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "login/icons8-exit-48.png")), size=(20, 20))
exit_icon_ios = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-ios-exit-100.png")), size=(20, 20))
secure_notebook_logo = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "icons8-secure-100.ico")),
    size=(26, 26))


def get_user_input(dialog_title, label_text, password=False):
    pin_storage = {'user_pin': None}

    def verify_pin(pin):
        if pin == "":
            messagebox.showerror("Błąd", "Podaj wartość")
            return
        pin_storage['user_pin'] = pin
        pin_dialog.grab_release()
        pin_dialog.destroy()

    pin_dialog = customtkinter.CTkToplevel()
    pin_dialog.title(dialog_title)
    pin_dialog.geometry("300x200")
    # pin_dialog.resizable(False, False)
    pin_dialog.iconbitmap(logo_image_path)

    pin_label = customtkinter.CTkLabel(pin_dialog, text=label_text,
                                       font=customtkinter.CTkFont(size=14))
    pin_label.pack(expand=True)

    pin_entry = customtkinter.CTkEntry(pin_dialog, show="*" if password else "")
    pin_entry.pack(expand=True)

    pin_dialog.grab_set()
    pin_dialog.after(100, pin_entry.focus_force)

    submit_button = customtkinter.CTkButton(pin_dialog, text="Potwierdź",
                                            command=lambda: verify_pin(pin_entry.get()))
    submit_button.pack(expand=True)

    pin_dialog.bind('<Return>', lambda event: verify_pin(pin_entry.get()))
    pin_dialog.bind('<Escape>', lambda event: pin_dialog.destroy())

    pin_dialog.update_idletasks()
    screen_width = pin_dialog.winfo_screenwidth()
    screen_height = pin_dialog.winfo_screenheight()
    x = (screen_width - pin_dialog.winfo_width()) // 2
    y = (screen_height - pin_dialog.winfo_height()) // 2
    pin_dialog.geometry("+{}+{}".format(x, y))

    pin_dialog.wait_window(pin_dialog)
    return pin_storage['user_pin']


def timestamp_to_date(timestamp):
    if timestamp is None:
        return "Nigdy"
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp)

    # Format the datetime object as a string
    date_string = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    return date_string
