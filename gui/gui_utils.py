import os
from PIL import Image
from tkinter import messagebox

import customtkinter

resource_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
dashboard_delete_note_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-remove-100.png")), size=(15, 15))
dashboard_edit_note_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-edit-100.png")), size=(15, 15))
dashboard_star_note_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-star-100.png")), size=(15, 15))
dashboard_star_filled_note_icon = customtkinter.CTkImage(
    dark_image=Image.open(os.path.join(resource_path, "dashboard/icons8-filled-star-100.png")), size=(15, 15))

def open_pin_dialog(title):
    pin_storage = {'user_pin': None}

    def verify_pin(pin):
        if pin == "":
            messagebox.showerror("Error", "PIN cannot be empty")
            return
        pin_storage['user_pin'] = pin
        pin_dialog.grab_release()
        pin_dialog.destroy()

    pin_dialog = customtkinter.CTkToplevel()
    pin_dialog.title("Enter PIN")
    pin_dialog.geometry("300x200")

    pin_label = customtkinter.CTkLabel(pin_dialog, text=title,
                                       font=customtkinter.CTkFont(size=14))
    pin_label.pack(expand=True)

    pin_entry = customtkinter.CTkEntry(pin_dialog, show="*")
    pin_entry.pack(expand=True)

    pin_dialog.grab_set()
    pin_dialog.focus_force()
    pin_entry.focus_force()

    submit_button = customtkinter.CTkButton(pin_dialog, text="Submit",
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
