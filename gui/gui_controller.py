import tkinter as tk
from tkinter import ttk, messagebox

class App:

    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")
        self.root.title("Football App")
        self.root.resizable(False, False)
        self.root.configure(background="#2a2a2a")
        # self.show_main_menu()


if __name__ == "__main__":
    print("GUI controller")
    main_window = tk.Tk()
    app = App(main_window)

    main_window.mainloop()
