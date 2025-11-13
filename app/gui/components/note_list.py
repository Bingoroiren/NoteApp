import customtkinter as ctk
from app.models.note_model import NoteModel

class NoteList(ctk.CTkScrollableFrame):
    def __init__(self, parent, on_note_select):
        super().__init__(parent, corner_radius=10)
        
        self.on_note_select = on_note_select
        self.note_model = NoteModel()
        self.note_widgets = []
    
    def load_notes(self, category=None):
        # Clear existing widgets
        for widget in self.note_widgets:
            widget.destroy()
        self.note_widgets.clear()
        
        # Load notes from database
        notes = self.note_model.read_all(category=category)
        
        if not notes:
            # Empty state
            empty_label = ctk.CTkLabel(
                self,
                text="Chưa có ghi chú nào\nThêm ghi chú mới để bắt đầu!",
                text_color="gray",
                font=("Segoe UI", 14)
            )
            empty_label.pack(expand=True)
            self.note_widgets.append(empty_label)
            return
        
        # Create note items
        for note in notes:
            note_frame = self.create_note_item(note)
            note_frame.pack(fill="x", pady=5)
            self.note_widgets.append(note_frame)
    
    def create_note_item(self, note):
        frame = ctk.CTkFrame(self, corner_radius=8, fg_color=("#2b2b2b", "#1f1f1f"))
        frame.bind("<Button-1>", lambda e: self.on_note_select(note["_id"]))
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            frame,
            text="",
            width=20,
            checkbox_width=20,
            checkbox_height=20,
            command=lambda: self.toggle_completed(note["_id"])
        )
        checkbox.pack(side="left", padx=10, pady=10)
        
        if note.get("completed"):
            checkbox.select()
        
        # Content
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, pady=10)
        
        title = note.get("title", "Không có tiêu đề")
        ctk.CTkLabel(
            content_frame,
            text=title,
            anchor="w",
            font=("Segoe UI", 13, "bold" if note.get("important") else "normal")
        ).pack(anchor="w")
        
        # Star icon if important
        if note.get("important"):
            ctk.CTkLabel(frame, text="⭐", font=("Segoe UI", 16)).pack(side="right", padx=10)
        
        return frame
    
    def toggle_completed(self, note_id):
        self.note_model.toggle_completed(note_id)
        self.load_notes()