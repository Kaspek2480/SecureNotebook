from tkinter import *

from gui.gui_utils import *
from shared.manager import *


class NoteEditor(customtkinter.CTkToplevel):
    def __init__(self, note_obj, exit_callback=None, *args, **kwargsj):
        super().__init__(*args, **kwargsj)

        self.iconbitmap(logo_image_path)
        self.note_obj = note_obj
        self.exit_callback = exit_callback
        self.note_content_before_edits = note_obj.content
        self.text_edited = False

        self.title(self.get_title_bar())
        self.geometry("900x600")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # bind user exit protocol
        self.protocol("WM_DELETE_WINDOW", self.handle_user_exit)

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=" Secure Notebook",
                                                             image=secure_notebook_logo,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"),
                                                             padx=10, pady=10)
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.textbox = customtkinter.CTkTextbox(self, width=250, height=100, border_color="gray70", border_width=1,
                                                fg_color="transparent")
        self.textbox.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.textbox.insert("1.0", self.note_obj.content)
        self.textbox.bind('<Control-s>', lambda event: self.save_note())
        self.textbox.bind('<Control-S>', lambda event: self.save_note())

        # trace any changes in textbox
        self.textbox.bind('<Key>', lambda event: self.text_changed_callback())

        # <editor-fold desc="navigation buttons">
        self.save_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                   border_spacing=10, text="Zapisz",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=dashboard_save_file_icon, anchor="w",
                                                   command=self.save_note)
        self.save_button.grid(row=1, column=0, sticky="ew")

        self.rollback_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Cofnij zmiany",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=dashboard_rollback_icon, anchor="w",
                                                       command=self.handle_note_revert)
        self.rollback_button.grid(row=2, column=0, sticky="ew")

        self.exit_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                   border_spacing=10, text="Zamknij",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=exit_icon_ios, anchor="w",
                                                   command=self.handle_user_exit)
        self.exit_button.grid(row=3, column=0, sticky="ew")
        # </editor-fold>

    def save_note(self):
        self.note_obj.content = self.get_note_textbox_content()
        update_note(self.note_obj)
        ensure_decrypted_note(self.note_obj)

        self.text_edited = False
        self.title(self.get_title_bar())

    def text_changed_callback(self):
        if not self.text_edited:
            self.text_edited = True
            self.title(self.get_title_bar())

    def close(self):
        self.textbox.destroy()
        super().destroy()

    def get_title_bar(self):
        if self.text_edited:
            return f"*{self.note_obj.title} - SecureNotebook"
        else:
            return f"{self.note_obj.title} - SecureNotebook"

    # restore all changes made to note content
    # but don't save it to database - user will decide if he wants to save changes or not
    def get_note_textbox_content(self):
        note_text = self.textbox.get('1.0', "end-1c")
        return note_text

    def handle_note_revert(self):
        # check if note content was changed
        if not self.is_note_modified():
            messagebox.showinfo("Brak zmian", "Nie dokonano żadnych zmian.")
            return

        if not messagebox.askyesno("Cofnij zmiany",
                                   "Za chwilę cofniesz wszystkie zmiany do momentu uruchomienia okna edycji notatki. "
                                   "Czy chcesz kontynuować?"):
            self.regain_focus()
            return

        self.textbox.delete("1.0", END)
        self.textbox.insert("1.0", self.note_content_before_edits)
        self.text_edited = True
        self.title(self.get_title_bar())

    def is_note_modified(self):
        return self.get_note_textbox_content() != self.note_content_before_edits

    def handle_user_exit(self):
        if self.text_edited:
            if not messagebox.askyesno("Zmiany nie zostały zapisane",
                                       "Czy na pewno chcesz zamknąć okno i porzucić zmiany?"):
                self.regain_focus()
                return

        # call exit callback (refresh notes list) only if user edited note
        if self.exit_callback is not None and self.is_note_modified():
            self.exit_callback()
        self.close()

    def regain_focus(self):
        self.after(100, self.lift)
        self.focus_set()
        self.textbox.focus_force()


# for testing purposes only
if __name__ == "__main__":
    n = Note(title="Test", content="Testowa notatka")
    print(n)

    note_editor = NoteEditor(n)
    note_editor.mainloop()
