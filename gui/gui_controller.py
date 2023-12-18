import sys
from os.path import abspath, dirname

# Add the 'shared' directory to the Python path
sys.path.append(abspath(dirname(dirname(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class App:

    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")
        self.root.title("Secure Notebook")
        self.root.resizable(False, False)
        self.root.configure(background="#2a2a2a")
        # self.show_main_menu()

        ico = Image.open('resources/app_icon.png')
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(False, photo)


if __name__ == "__main__":
    print("GUI controller")
    main_window = tk.Tk()
    app = App(main_window)

    main_window.iconbitmap("resources/app_icon.ico")
    main_window.mainloop()
