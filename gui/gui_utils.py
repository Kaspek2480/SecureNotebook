from tkinter import messagebox

import customtkinter


def open_pin_dialog():
    pin_storage = {'user_pin': None}

    def verify_pin(pin):
        if pin == "":
            messagebox.showerror("Error", "PIN cannot be empty")
            return
        pin_storage['user_pin'] = pin  # store the entered pin
        print("Entered PIN:", pin_storage['user_pin'])
        pin_dialog.grab_release()  # enable interaction with other windows after pin verification
        pin_dialog.destroy()  # close the pin dialog

    pin_dialog = customtkinter.CTkToplevel()
    pin_dialog.title("Enter PIN")
    pin_dialog.geometry("300x200")
    pin_dialog.grab_set()  # disable interaction with other windows

    pin_label = customtkinter.CTkLabel(pin_dialog, text="Please enter the PIN",
                                       font=customtkinter.CTkFont(size=14))
    pin_label.pack(expand=True)

    pin_entry = customtkinter.CTkEntry(pin_dialog, show="*")
    pin_entry.pack(expand=True)

    submit_button = customtkinter.CTkButton(pin_dialog, text="Submit",
                                            command=lambda: verify_pin(pin_entry.get()))
    submit_button.pack(expand=True)

    pin_dialog.bind('<Return>', lambda event: verify_pin(pin_entry.get()))

    pin_dialog.update_idletasks()
    screen_width = pin_dialog.winfo_screenwidth()
    screen_height = pin_dialog.winfo_screenheight()
    x = (screen_width - pin_dialog.winfo_width()) // 2
    y = (screen_height - pin_dialog.winfo_height()) // 2
    pin_dialog.geometry("+{}+{}".format(x, y))

    # Make the function wait until the window is destroyed, then return the PIN
    pin_dialog.wait_window(pin_dialog)
    return pin_storage['user_pin']
