import tkinter as tk
from customtkinter import CTkButton

class MainFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        button = CTkButton(self, text="Go to other frame", command=self.master.switch_frame(OtherFrame))
        button.pack(pady=10)

class OtherFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        button = CTkButton(self, text="Go back", command=self.master.switch_frame(MainFrame))
        button.pack(pady=10)

class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(MainFrame)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()