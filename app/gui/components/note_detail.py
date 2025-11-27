"""
Note detail component for viewing and editing notes
"""
import customtkinter as ctk
from typing import Callable, Dict
from datetime import datetime
import logging
from tkinter import filedialog
import os

logger = logging.getLogger(__name__)


class NoteDetail(ctk.CTkFrame):
    """Detailed view and editor for a single note"""
    
    def __init__(self, parent, on_update: Callable, on_attachment_add: Callable):
        super().__init__(parent, fg_color="gray20", corner_radius=10)
        
        self.on_update = on_update
        self.on_attachment_add = on_attachment_add
        
        self.current_note = None
        self.is_editing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the detail view UI"""
        # Configure grid
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header with actions
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title (editable)
        self.title_entry = ctk.CTkEntry(
            self.header_frame,
            font=("Arial", 24, "bold"),
            placeholder_text="Note Title",
            height=40,
            border_width=0,
            fg_color="transparent"
        )
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.title_entry.bind("<FocusOut>", self.save_title)
        
        # Action buttons
        action_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        action_frame.grid(row=0, column=1, sticky="e")
        
        self.star_btn = ctk.CTkButton(
            action_frame,
            text="☆",
            width=40,
            height=40,
            font=("Arial", 18),
            fg_color="transparent",
            hover_color="gray30",
            command=self.toggle_star
        )
        self.star_btn.pack(side="left", padx=2)
        
        archive_btn = ctk.CTkButton(
            action_frame,
            text="📦",
            width=40,
            height=40,
            font=("Arial", 18),
            fg_color="transparent",
            hover_color="gray30",
            command=self.archive_note
        )
        archive_btn.pack(side="left", padx=2)
        
        export_btn = ctk.CTkButton(
            action_frame,
            text="📤",
            width=40,
            height=40,
            font=("Arial", 18),
            fg_color="transparent",
            hover_color="gray30",
            command=self.export_note
        )
        export_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=40,
            height=40,
            font=("Arial", 18),
            fg_color="transparent",
            hover_color="gray30",
            text_color="#DC2626",
            command=self.delete_note
        )
        delete_btn.pack(side="left", padx=2)
        
        # Metadata bar
        self.metadata_frame = ctk.CTkFrame(self, fg_color="gray25", height=50)
        self.metadata_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.metadata_frame.grid_columnconfigure(3, weight=1)
        
        # Category
        ctk.CTkLabel(
            self.metadata_frame,
            text="📁",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=(15, 5), pady=10)
        
        self.category_var = ctk.StringVar(value="General")
        self.category_menu = ctk.CTkOptionMenu(
            self.metadata_frame,
            variable=self.category_var,
            values=["General", "Work", "Personal", "Ideas", "Tasks"],
            width=120,
            height=30,
            command=self.update_category
        )
        self.category_menu.grid(row=0, column=1, padx=5, pady=10)
        
        # Priority
        ctk.CTkLabel(
            self.metadata_frame,
            text="🎯",
            font=("Arial", 14)
        ).grid(row=0, column=2, padx=(15, 5), pady=10)
        
        self.priority_var = ctk.StringVar(value="medium")
        self.priority_menu = ctk.CTkOptionMenu(
            self.metadata_frame,
            variable=self.priority_var,
            values=["low", "medium", "high", "urgent"],
            width=100,
            height=30,
            command=self.update_priority
        )
        self.priority_menu.grid(row=0, column=3, padx=5, pady=10)
        
        # Date info
        self.date_label = ctk.CTkLabel(
            self.metadata_frame,
            text="",
            font=("Arial", 11),
            text_color="gray50"
        )
        self.date_label.grid(row=0, column=4, padx=15, pady=10, sticky="e")
        
        # Content area (scrollable)
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Content textbox
        self.content_text = ctk.CTkTextbox(
            self.content_frame,
            font=("Arial", 13),
            wrap="word",
            border_width=0,
            fg_color="transparent"
        )
        self.content_text.grid(row=0, column=0, sticky="nsew", pady=10)
        self.content_text.bind("<KeyRelease>", self.auto_save_content)
        
        # Tags section
        tags_frame = ctk.CTkFrame(self.content_frame, fg_color="gray25", corner_radius=8)
        tags_frame.grid(row=1, column=0, sticky="ew", pady=10)
        
        ctk.CTkLabel(
            tags_frame,
            text="🏷️ Tags:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=15, pady=10)
        
        self.tags_entry = ctk.CTkEntry(
            tags_frame,
            placeholder_text="Add tags (separated by comma)",
            height=35,
            border_width=0,
            fg_color="gray20"
        )
        self.tags_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.tags_entry.bind("<Return>", self.update_tags)
        
        # Attachments section
        attachments_frame = ctk.CTkFrame(self.content_frame, fg_color="gray25", corner_radius=8)
        attachments_frame.grid(row=2, column=0, sticky="ew", pady=10)
        attachments_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            attachments_frame,
            text="📎 Attachments:",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        add_attachment_btn = ctk.CTkButton(
            attachments_frame,
            text="+ Add File",
            width=100,
            height=30,
            command=self.add_attachment
        )
        add_attachment_btn.grid(row=0, column=1, padx=15, pady=10, sticky="e")
        
        # Attachments list
        self.attachments_frame = ctk.CTkFrame(attachments_frame, fg_color="transparent")
        self.attachments_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))
        
        # Footer with word count
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.word_count_label = ctk.CTkLabel(
            footer_frame,
            text="Words: 0 | Characters: 0",
            font=("Arial", 11),
            text_color="gray50"
        )
        self.word_count_label.pack(side="left")
        
        self.save_status_label = ctk.CTkLabel(
            footer_frame,
            text="",
            font=("Arial", 11),
            text_color="gray50"
        )
        self.save_status_label.pack(side="right")
        
        # Show empty state
        self.show_empty_state()
    
    def display_note(self, note: Dict):
        """Display a note's details"""
        self.current_note = note
        
        # Hide empty state
        if hasattr(self, 'empty_label') and self.empty_label:
            self.empty_label.destroy()
            self.empty_label = None
        
        # Update title
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note.get('title', ''))
        
        # Update star
        star_icon = "⭐" if note.get('is_starred') else "☆"
        self.star_btn.configure(text=star_icon)
        
        # Update metadata
        self.category_var.set(note.get('category', 'General'))
        self.priority_var.set(note.get('priority', 'medium'))
        
        # Update date
        created = note.get('created_date')
        updated = note.get('updated_date')
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        if isinstance(updated, str):
            updated = datetime.fromisoformat(updated)
        
        date_text = f"Created: {created.strftime('%b %d, %Y')}"
        if updated:
            date_text += f" | Updated: {updated.strftime('%b %d, %Y')}"
        self.date_label.configure(text=date_text)
        
        # Update content
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", note.get('content', ''))
        
        # Update tags
        tags = note.get('tags', [])
        self.tags_entry.delete(0, "end")
        if tags:
            self.tags_entry.insert(0, ", ".join(tags))
        
        # Update attachments
        self.display_attachments(note.get('attachment_list', []))
        
        # Update word count
        self.update_word_count()
        
        logger.info(f"Displaying note: {note['_id']}")
    
    def display_attachments(self, attachments: list):
        """Display attachments"""
        # Clear existing
        for widget in self.attachments_frame.winfo_children():
            widget.destroy()
        
        if not attachments:
            no_attach_label = ctk.CTkLabel(
                self.attachments_frame,
                text="No attachments",
                font=("Arial", 11),
                text_color="gray50"
            )
            no_attach_label.pack(pady=10)
            return
        
        for attachment in attachments:
            attach_item = ctk.CTkFrame(self.attachments_frame, fg_color="gray20", corner_radius=5)
            attach_item.pack(fill="x", pady=5)
            
            # File icon
            file_type = attachment.get('filetype', '').lower()
            icon = self.get_file_icon(file_type)
            
            ctk.CTkLabel(
                attach_item,
                text=icon,
                font=("Arial", 16)
            ).pack(side="left", padx=10)
            
            # Filename
            filename = attachment.get('filename', 'Unknown')
            ctk.CTkLabel(
                attach_item,
                text=filename,
                font=("Arial", 12),
                anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=5)
            
            # File size
            filesize = attachment.get('filesize', 0)
            size_text = self.format_file_size(filesize)
            ctk.CTkLabel(
                attach_item,
                text=size_text,
                font=("Arial", 10),
                text_color="gray50"
            ).pack(side="right", padx=10)
    
    def get_file_icon(self, file_type: str) -> str:
        """Get icon for file type"""
        icons = {
            '.pdf': '📄',
            '.doc': '📝',
            '.docx': '📝',
            '.xls': '📊',
            '.xlsx': '📊',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️'
        }
        return icons.get(file_type, '📎')
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} GB"
    
    def save_title(self, event=None):
        """Save title when focus lost"""
        if not self.current_note:
            return
        
        new_title = self.title_entry.get().strip()
        if new_title and new_title != self.current_note.get('title'):
            self.on_update(self.current_note['_id'], title=new_title)
            self.show_save_status("Title saved")
    
    def auto_save_content(self, event=None):
        """Auto-save content after typing"""
        if not self.current_note:
            return
        
        self.update_word_count()
        
        # Debounce save (wait for typing to stop)
        if hasattr(self, 'save_timer'):
            self.after_cancel(self.save_timer)
        
        self.save_timer = self.after(1000, self.save_content)
    
    def save_content(self):
        """Save content to database"""
        if not self.current_note:
            return
        
        new_content = self.content_text.get("1.0", "end-1c")
        if new_content != self.current_note.get('content'):
            self.on_update(self.current_note['_id'], content=new_content)
            self.show_save_status("Saved")
    
    def update_category(self, value):
        """Update note category"""
        if self.current_note:
            self.on_update(self.current_note['_id'], category=value)
    
    def update_priority(self, value):
        """Update note priority"""
        if self.current_note:
            self.on_update(self.current_note['_id'], priority=value)
    
    def update_tags(self, event=None):
        """Update note tags"""
        if not self.current_note:
            return
        
        tags_text = self.tags_entry.get().strip()
        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        self.on_update(self.current_note['_id'], tags=tags)
        self.show_save_status("Tags updated")
    
    def toggle_star(self):
        """Toggle star status"""
        if self.current_note:
            self.on_update(self.current_note['_id'], 
                         is_starred=not self.current_note.get('is_starred', False))
    
    def archive_note(self):
        """Archive current note"""
        if self.current_note:
            self.on_update(self.current_note['_id'], 
                         is_archived=not self.current_note.get('is_archived', False))
    
    def delete_note(self):
        """Delete current note"""
        # TODO: Add confirmation dialog
        logger.info("Delete note clicked")
    
    def export_note(self):
        """Export current note"""
        # TODO: Implement export
        logger.info("Export note clicked")
    
    def add_attachment(self):
        """Add an attachment"""
        if not self.current_note:
            return
        
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("All Files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("Documents", "*.pdf *.doc *.docx"),
                ("Spreadsheets", "*.xls *.xlsx")
            ]
        )
        
        if file_path:
            self.on_attachment_add(self.current_note['_id'], file_path)
    
    def update_word_count(self):
        """Update word and character count"""
        content = self.content_text.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        
        self.word_count_label.configure(text=f"Words: {words} | Characters: {chars}")
    
    def show_save_status(self, message: str):
        """Show save status message"""
        self.save_status_label.configure(text=message)
        self.after(2000, lambda: self.save_status_label.configure(text=""))
    
    def show_empty_state(self):
        """Show empty state when no note selected"""
        self.empty_label = ctk.CTkLabel(
            self,
            text="📝\n\nSelect a note to view details\n\nor create a new note",
            font=("Arial", 16),
            text_color="gray50",
            justify="center"
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def clear(self):
        """Clear the detail view"""
        self.current_note = None
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        self.tags_entry.delete(0, "end")
        self.show_empty_state()