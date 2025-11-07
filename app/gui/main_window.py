import customtkinter as ctk
from datetime import datetime
from app.gui.components.sidebar import Sidebar
from app.models.note_model import NoteModel


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ===== WINDOW =====
        self.title("NOTES APP")
        self.geometry("1100x700")
        self.configure(fg_color=("#1E1E1E", "#1E1E1E"))

        # ===== MODEL =====
        self.note_model = NoteModel()

        # ===== GRID =====
        self.grid_columnconfigure(0, weight=0)   # sidebar
        self.grid_columnconfigure(1, weight=1)   # main
        self.grid_rowconfigure(0, weight=1)

        # ===== STATE =====
        self.current_category = "Ngày của Tôi"

        # ===== SIDEBAR =====
        self.sidebar = Sidebar(self, self.on_category_change, auto_select=False)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # ===== MAIN =====
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header, text="My Day",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        self.date_label = ctk.CTkLabel(
            header, text=self.get_current_date(),
            font=ctk.CTkFont(size=16), text_color="#BBBBBB"
        )
        self.date_label.pack(anchor="w", padx=10, pady=(0, 10))

        # List
        self.list_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#494545")
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 20))
        self.note_widgets = []

        # Add bar
        add_bar = ctk.CTkFrame(self.main_frame, fg_color="#F9FAFB", corner_radius=25)
        add_bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.add_entry = ctk.CTkEntry(
            add_bar, placeholder_text="Add a task",
            height=40, corner_radius=25, font=ctk.CTkFont(size=14)
        )
        self.add_entry.pack(side="left", padx=(15, 10), pady=10, fill="x", expand=True)
        self.add_entry.bind("<Return>", self.on_add_task)

        self.add_btn = ctk.CTkButton(
            add_bar, text="Thêm", width=90, height=38, corner_radius=20,
            fg_color="#3B82F6", hover_color="#2563EB", text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"), command=self.on_add_task
        )
        self.add_btn.pack(side="right", padx=(0, 15), pady=10)

        # Initial data
        self.sidebar.select_category("Ngày của Tôi")
        self.load_notes()

    # ===== Helpers =====
    def get_current_date(self) -> str:
        return datetime.now().strftime("%A, %B %d")

    def clear_widgets(self):
        for w in self.note_widgets:
            w.destroy()
        self.note_widgets.clear()

    def load_notes(self):
        self.clear_widgets()
        category = "My Day" if self.current_category == "Ngày của Tôi" else self.current_category
        notes = self.note_model.read_all(category=category)

        if not notes:
            lbl = ctk.CTkLabel(
                self.list_frame,
                text="Chưa có ghi chú nào\nThêm ghi chú mới để bắt đầu!",
                font=ctk.CTkFont(size=14), text_color="#888888", justify="center"
            )
            lbl.pack(pady=20)
            self.note_widgets.append(lbl)
            return

        for note in notes:
            self._add_note_widget(note)

    def _add_note_widget(self, note):
        row = ctk.CTkFrame(self.list_frame, fg_color="#F9FAFB", corner_radius=10)
        row.pack(fill="x", padx=10, pady=5)

        var = ctk.BooleanVar(value=note.get("completed", False))
        cb = ctk.CTkCheckBox(
            row, text=note.get("title", "Untitled"), variable=var,
            font=ctk.CTkFont(size=15), onvalue=True, offvalue=False,
            command=lambda n=note: self.toggle_completed(n)
        )
        cb.pack(anchor="w", padx=15, pady=10, fill="x", expand=True)

        if note.get("completed", False):
            cb.configure(font=ctk.CTkFont(size=15, overstrike=True))

        self.note_widgets.append(row)

    def on_add_task(self, event=None):
        title = self.add_entry.get().strip()
        if not title:
            return
        self.note_model.create(title=title, category="My Day")
        self.add_entry.delete(0, "end")
        self.load_notes()

    def toggle_completed(self, note):
        self.note_model.toggle_completed(note["_id"])
        self.load_notes()

    def on_category_change(self, category: str):
        self.current_category = category
        self.load_notes()
