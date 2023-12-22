from tkinter import *
import customtkinter

from shared.database import Note


class NoteEditor(customtkinter.CTk):
    def __init__(self, note_obj):
        super().__init__()

        self.iconbitmap("resources/icons8-secure-100.ico")
        self.note_obj = note_obj
        self.text_edited = False

        self.title(self.get_title_bar())
        self.geometry("500x500")
        self.resizable(False, False)

        # set grid layout 1x3
        self.grid_rowconfigure(0, weight=1)
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)

        # self.textbox = customtkinter.CTkTextbox(self, width=250, height=250, border_color="gray70", border_width=1,
        #                                         fg_color="transparent")
        # self.textbox.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.textbox = customtkinter.CTkTextbox(self, width=100)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        self.textbox.insert("1.0", self.note_obj.content)
        self.textbox.focus_force()
        self.textbox.bind('<Escape>', lambda event: self.destroy())
        self.textbox.bind('<Control-s>', lambda event: self.save_note())
        self.textbox.bind('<Control-S>', lambda event: self.save_note())
        # trace if user changes text in textbox
        self.textbox.bind('<Key>', lambda event: self.text_changed())

        # Center the textbox in the first column
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)



        self.save_button = customtkinter.CTkButton(self, text="Zapisz", width=10, height=10, border_color="gray70",
                                                   border_width=1, fg_color="transparent",
                                                   text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   command=self.save_note)
        self.save_button.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.cancel_button = customtkinter.CTkButton(self, text="Anuluj", width=10, height=10, border_color="gray70",
                                                     border_width=1, fg_color="transparent",
                                                     text_color=("gray10", "gray90"),
                                                     hover_color=("gray70", "gray30"),
                                                     command=self.destroy)
        self.cancel_button.grid(row=0, column=2, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.winfo_width()) // 2
        y = (screen_height - self.winfo_height()) // 2
        self.geometry("+{}+{}".format(x, y))

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def save_note(self):
        self.text_edited = False
        self.title(self.get_title_bar())

    def text_changed(self):
        if not self.text_edited:
            self.text_edited = True
            self.title(self.get_title_bar())

    def close(self):
        self.note_text.destroy()
        super().destroy()

    def get_title_bar(self):
        if self.text_edited:
            return f"*{self.note_obj.title} - SecureNotebook"
        else:
            return f"{self.note_obj.title} - SecureNotebook"

    def get_note_text(self):
        print(self.textbox.get('1.0', END))


if __name__ == "__main__":
    n = Note(title="Test", content="XD")
    print(n)
    note_editor = NoteEditor(n)
    note_editor.mainloop()
