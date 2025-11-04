#màn chính
import customtkinter as ctk
from app.gui.components.sidebar import Sidebar
from app.gui.components.note_list import NoteList
from app.gui.components.note_detail import NoteDetail
from app.models.database import Database

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window config
        self.title("NOTEAPP")
        self.geometry("1200x700")
        
        # Connect database
        self.db = Database()
        self.db.connect()
        
        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Current category
        self.current_category = "Ngày của Tôi"
        
        # Create components
        self.sidebar = Sidebar(self, self.on_category_change, auto_select=False)
        self.note_list = NoteList(self, self.on_note_select)
        self.note_detail = NoteDetail(self)
        
        # Place components
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.note_list.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.note_detail.grid(row=0, column=2, sticky="nsew", padx=(0, 10), pady=10)
        
        # Load initial data
        self.sidebar.select_category("Ngày của Tôi")
        self.load_notes()
    
    def on_category_change(self, category):
        self.current_category = category
        self.load_notes()
    
    def on_note_select(self, note_id):
        self.note_detail.load_note(note_id)
    
    def load_notes(self):
        category = None if self.current_category == "Ngày của Tôi" else self.current_category
        self.note_list.load_notes(category=category)
    
    def destroy(self):
        self.db.close()
        super().destroy()