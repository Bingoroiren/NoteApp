"""
NoteApp - Advanced Note Taking Application
Main entry point
"""
import customtkinter as ctk
import os
import sys
from dotenv import load_dotenv
import logging

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('noteapp.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import after path setup
from app.models.database import db_instance
from app.controllers.note_controller import NoteController
from app.gui.components.sidebar import Sidebar
from app.gui.components.note_list import NoteList
from app.gui.components.note_detail import NoteDetail
from app.gui.components.add_note import AddNoteDialog


class NoteApp(ctk.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("NoteApp - Advanced Note Taking")
        self.geometry("1400x800")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize controller
        self.controller = NoteController()
        
        # Check database connection
        if not db_instance.test_connection():
            self.show_error("Database connection failed. Please check MongoDB.")
            return
        
        # Current state
        self.current_filter = "all"
        self.current_note_id = None
        self.selected_notes = []
        
        # Setup UI
        self.setup_ui()
        
        # Load notes
        self.refresh_notes()
        
        logger.info("NoteApp started successfully")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main containers
        self.sidebar = Sidebar(self, self.on_filter_change)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Right panel
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid_columnconfigure(1, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Top bar
        top_bar = ctk.CTkFrame(right_panel, height=60)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        top_bar.grid_columnconfigure(1, weight=1)
        
        # Search
        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="🔍 Search notes...",
            height=40,
            font=("Arial", 14)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Add note button
        add_btn = ctk.CTkButton(
            top_bar,
            text="+ New Note",
            width=140,
            height=40,
            font=("Arial", 14, "bold"),
            command=self.add_note
        )
        add_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Note list
        self.note_list = NoteList(
            right_panel,
            self.on_note_select,
            self.on_star_click,
            self.on_note_delete
        )
        self.note_list.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # Note detail
        self.note_detail = NoteDetail(
            right_panel,
            self.on_note_update,
            self.on_attachment_add
        )
        self.note_detail.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        
        # Configure right panel grid weights
        right_panel.grid_columnconfigure(0, weight=2, minsize=400)
        right_panel.grid_columnconfigure(1, weight=3, minsize=600)
    
    def refresh_notes(self):
        """Refresh the note list"""
        try:
            if self.current_filter == "all":
                notes = self.controller.get_all_notes(include_archived=False)
            elif self.current_filter == "starred":
                notes = self.controller.note_model.get_starred_notes()
            elif self.current_filter == "archived":
                notes = self.controller.note_model.get_archived_notes()
            elif self.current_filter.startswith("category:"):
                category = self.current_filter.split(":")[1]
                notes = self.controller.note_model.get_notes_by_category(category)
            elif self.current_filter.startswith("priority:"):
                priority = self.current_filter.split(":")[1]
                notes = self.controller.note_model.get_notes_by_priority(priority)
            else:
                notes = self.controller.get_all_notes()
            
            self.note_list.update_notes(notes)
            
            # Update sidebar statistics
            stats = self.controller.get_statistics()
            self.sidebar.update_stats(stats)
            
        except Exception as e:
            logger.error(f"Error refreshing notes: {str(e)}")
            self.show_error("Failed to refresh notes")
    
    def on_filter_change(self, filter_type: str):
        """Handle filter change"""
        self.current_filter = filter_type
        self.refresh_notes()
    
    def on_search(self, event=None):
        """Handle search"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.refresh_notes()
            return
        
        try:
            notes = self.controller.search_notes(search_term)
            self.note_list.update_notes(notes)
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
    
    def add_note(self):
        """Open add note dialog"""
        dialog = AddNoteDialog(self, self.controller)
        self.wait_window(dialog)
        
        # Refresh after adding
        self.refresh_notes()
    
    def on_note_select(self, note_id: str):
        """Handle note selection"""
        self.current_note_id = note_id
        
        try:
            note = self.controller.get_note(note_id)
            if note:
                self.note_detail.display_note(note)
        except Exception as e:
            logger.error(f"Error loading note: {str(e)}")
            self.show_error("Failed to load note")
    
    def on_note_update(self, note_id: str, **kwargs):
        """Handle note update"""
        try:
            if self.controller.update_note(note_id, **kwargs):
                self.refresh_notes()
                # Reload the note detail
                note = self.controller.get_note(note_id)
                if note:
                    self.note_detail.display_note(note)
        except Exception as e:
            logger.error(f"Error updating note: {str(e)}")
            self.show_error("Failed to update note")
    
    def on_star_click(self, note_id: str):
        """Handle star toggle"""
        try:
            if self.controller.toggle_star(note_id):
                self.refresh_notes()
                # Update detail view if this is the current note
                if self.current_note_id == note_id:
                    note = self.controller.get_note(note_id)
                    if note:
                        self.note_detail.display_note(note)
        except Exception as e:
            logger.error(f"Error toggling star: {str(e)}")
    
    def on_note_delete(self, note_id: str):
        """Handle note deletion"""
        try:
            if self.controller.delete_note(note_id):
                self.refresh_notes()
                # Clear detail view if this was the current note
                if self.current_note_id == note_id:
                    self.note_detail.clear()
                    self.current_note_id = None
        except Exception as e:
            logger.error(f"Error deleting note: {str(e)}")
            self.show_error("Failed to delete note")
    
    def on_attachment_add(self, note_id: str, file_path: str):
        """Handle attachment addition"""
        try:
            attachment_id = self.controller.add_attachment(note_id, file_path)
            if attachment_id:
                # Reload note to show new attachment
                note = self.controller.get_note(note_id)
                if note:
                    self.note_detail.display_note(note)
            else:
                self.show_error("Failed to add attachment")
        except Exception as e:
            logger.error(f"Error adding attachment: {str(e)}")
            self.show_error("Failed to add attachment")
    
    def show_error(self, message: str):
        """Show error message"""
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(
            title="Error",
            message=message,
            icon="cancel"
        )
    
    def on_closing(self):
        """Handle window closing"""
        logger.info("Closing NoteApp")
        db_instance.close_connection()
        self.destroy()


def main():
    """Main entry point"""
    try:
        app = NoteApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"Error starting application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()