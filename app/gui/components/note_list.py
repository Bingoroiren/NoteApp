"""
Note list component for displaying notes
"""
import customtkinter as ctk
from typing import Callable, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NoteListItem(ctk.CTkFrame):
    """Individual note list item"""
    
    def __init__(self, parent, note: Dict, on_click: Callable, 
                 on_star: Callable, on_delete: Callable):
        super().__init__(parent, fg_color="gray20", corner_radius=10, height=120)
        
        self.note = note
        self.on_click = on_click
        self.on_star = on_star
        self.on_delete = on_delete
        
        self.grid_propagate(False)
        self.setup_ui()
        
        # Bind click event
        self.bind("<Button-1>", lambda e: self.on_click(self.note['_id']))
    
    def setup_ui(self):
        """Setup the note item UI"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Priority indicator (left bar)
        priority = self.note.get('priority', 'medium')
        priority_colors = {
            'urgent': '#DC2626',
            'high': '#EA580C',
            'medium': '#CA8A04',
            'low': '#16A34A'
        }
        
        priority_bar = ctk.CTkFrame(
            self,
            width=4,
            fg_color=priority_colors.get(priority, '#CA8A04'),
            corner_radius=0
        )
        priority_bar.grid(row=0, column=0, rowspan=3, sticky="ns", padx=(0, 10))
        
        # Title and star
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=1, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            header_frame,
            text=self.note.get('title', 'Untitled'),
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w")
        title.bind("<Button-1>", lambda e: self.on_click(self.note['_id']))
        
        # Star button
        star_icon = "⭐" if self.note.get('is_starred') else "☆"
        star_btn = ctk.CTkButton(
            header_frame,
            text=star_icon,
            width=30,
            height=30,
            font=("Arial", 16),
            fg_color="transparent",
            hover_color="gray30",
            command=lambda: self.on_star(self.note['_id'])
        )
        star_btn.grid(row=0, column=1, padx=5)
        
        # Content preview
        content = self.note.get('content', '')
        preview = content[:100] + "..." if len(content) > 100 else content
        
        content_label = ctk.CTkLabel(
            self,
            text=preview,
            font=("Arial", 12),
            text_color="gray70",
            anchor="w",
            justify="left",
            wraplength=350
        )
        content_label.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        content_label.bind("<Button-1>", lambda e: self.on_click(self.note['_id']))
        
        # Footer with metadata
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=1, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Tags
        tags = self.note.get('tags', [])
        if tags:
            tags_text = " ".join([f"#{tag}" for tag in tags[:3]])
            tags_label = ctk.CTkLabel(
                footer_frame,
                text=tags_text,
                font=("Arial", 10),
                text_color="gray50"
            )
            tags_label.grid(row=0, column=0, sticky="w")
        
        # Date
        created_date = self.note.get('created_date')
        if created_date:
            date_str = self.format_date(created_date)
            date_label = ctk.CTkLabel(
                footer_frame,
                text=date_str,
                font=("Arial", 10),
                text_color="gray50"
            )
            date_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
        
        # Category badge
        category = self.note.get('category', 'General')
        category_label = ctk.CTkLabel(
            footer_frame,
            text=f"📁 {category}",
            font=("Arial", 10),
            text_color="gray50"
        )
        category_label.grid(row=0, column=2, sticky="e", padx=(10, 0))
    
    def format_date(self, date) -> str:
        """Format date for display"""
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date)
            except:
                return date
        
        now = datetime.now()
        diff = now - date
        
        if diff.days == 0:
            if diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes}m ago"
            else:
                hours = diff.seconds // 3600
                return f"{hours}h ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days}d ago"
        else:
            return date.strftime("%b %d")


class NoteList(ctk.CTkScrollableFrame):
    """Scrollable list of notes"""
    
    def __init__(self, parent, on_note_click: Callable, 
                 on_star_click: Callable, on_delete: Callable):
        super().__init__(parent, fg_color="transparent")
        
        self.on_note_click = on_note_click
        self.on_star_click = on_star_click
        self.on_delete = on_delete
        
        self.notes = []
        self.note_widgets = []
        
        # Empty state
        self.empty_label = None
        self.show_empty_state()
    
    def update_notes(self, notes: List[Dict]):
        """Update the list of notes"""
        self.notes = notes
        
        # Clear existing widgets
        for widget in self.note_widgets:
            widget.destroy()
        self.note_widgets.clear()
        
        if self.empty_label:
            self.empty_label.destroy()
            self.empty_label = None
        
        if not notes:
            self.show_empty_state()
            return
        
        # Create note items
        for note in notes:
            item = NoteListItem(
                self,
                note,
                self.on_note_click,
                self.on_star_click,
                self.on_delete
            )
            item.pack(fill="x", padx=10, pady=5)
            self.note_widgets.append(item)
        
        logger.info(f"Displayed {len(notes)} notes")
    
    def show_empty_state(self):
        """Show empty state when no notes"""
        self.empty_label = ctk.CTkLabel(
            self,
            text="📝\n\nNo notes yet\n\nClick '+ New Note' to create your first note",
            font=("Arial", 14),
            text_color="gray50",
            justify="center"
        )
        self.empty_label.pack(expand=True, pady=100)
    
    def get_selected_notes(self) -> List[str]:
        """Get list of selected note IDs"""
        # TODO: Implement multi-select functionality
        return []
    
    def select_note(self, note_id: str):
        """Highlight a specific note"""
        for widget in self.note_widgets:
            if hasattr(widget, 'note') and widget.note['_id'] == note_id:
                widget.configure(fg_color="gray30")
            else:
                widget.configure(fg_color="gray20")
    
    def clear_selection(self):
        """Clear all selections"""
        for widget in self.note_widgets:
            widget.configure(fg_color="gray20")