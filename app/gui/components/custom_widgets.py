"""
Custom widgets for the application
"""
import customtkinter as ctk
from typing import Callable, List
import tkinter as tk
from datetime import datetime


class TagInput(ctk.CTkFrame):
    """Custom tag input widget with pills"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="gray20", corner_radius=8, **kwargs)
        
        self.tags = []
        self.tag_widgets = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the tag input UI"""
        # Input entry
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="Add tag and press Enter...",
            height=35,
            border_width=0,
            fg_color="transparent"
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.entry.bind("<Return>", self.add_tag)
        
        # Tags container (will be created dynamically)
        self.tags_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tags_frame.pack(side="left", padx=5)
    
    def add_tag(self, event=None):
        """Add a new tag"""
        tag_text = self.entry.get().strip()
        
        if tag_text and tag_text not in self.tags:
            self.tags.append(tag_text)
            self.create_tag_pill(tag_text)
            self.entry.delete(0, "end")
    
    def create_tag_pill(self, tag: str):
        """Create a tag pill widget"""
        pill = ctk.CTkFrame(self.tags_frame, fg_color="blue", corner_radius=15, height=25)
        pill.pack(side="left", padx=2, pady=2)
        
        # Tag label
        label = ctk.CTkLabel(
            pill,
            text=f"#{tag}",
            font=("Arial", 11),
            text_color="white"
        )
        label.pack(side="left", padx=(10, 5), pady=2)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            pill,
            text="×",
            width=20,
            height=20,
            font=("Arial", 14),
            fg_color="transparent",
            hover_color="darkblue",
            command=lambda: self.remove_tag(tag, pill)
        )
        remove_btn.pack(side="right", padx=(0, 5))
        
        self.tag_widgets.append(pill)
    
    def remove_tag(self, tag: str, widget):
        """Remove a tag"""
        if tag in self.tags:
            self.tags.remove(tag)
        
        widget.destroy()
        
        if widget in self.tag_widgets:
            self.tag_widgets.remove(widget)
    
    def get_tags(self) -> List[str]:
        """Get all tags"""
        return self.tags.copy()
    
    def set_tags(self, tags: List[str]):
        """Set tags"""
        # Clear existing
        self.clear_tags()
        
        # Add new tags
        for tag in tags:
            if tag and tag not in self.tags:
                self.tags.append(tag)
                self.create_tag_pill(tag)
    
    def clear_tags(self):
        """Clear all tags"""
        self.tags.clear()
        
        for widget in self.tag_widgets:
            widget.destroy()
        
        self.tag_widgets.clear()


class ColorPicker(ctk.CTkFrame):
    """Custom color picker widget"""
    
    def __init__(self, parent, on_color_select: Callable = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_color_select = on_color_select
        self.selected_color = "#FFFFFF"
        
        self.colors = [
            ("#FFFFFF", "White"),
            ("#FEF3C7", "Yellow"),
            ("#DBEAFE", "Blue"),
            ("#D1FAE5", "Green"),
            ("#FCE7F3", "Pink"),
            ("#F3E8FF", "Purple"),
            ("#FEE2E2", "Red"),
            ("#F3F4F6", "Gray")
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the color picker UI"""
        for color, name in self.colors:
            btn = ctk.CTkButton(
                self,
                text="",
                width=40,
                height=40,
                fg_color=color,
                hover_color=color,
                border_width=2,
                border_color="gray40",
                corner_radius=8,
                command=lambda c=color: self.select_color(c)
            )
            btn.pack(side="left", padx=5)
    
    def select_color(self, color: str):
        """Select a color"""
        self.selected_color = color
        
        if self.on_color_select:
            self.on_color_select(color)
    
    def get_color(self) -> str:
        """Get selected color"""
        return self.selected_color
    
    def set_color(self, color: str):
        """Set selected color"""
        self.selected_color = color


class PriorityPicker(ctk.CTkFrame):
    """Custom priority picker widget"""
    
    def __init__(self, parent, on_priority_select: Callable = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_priority_select = on_priority_select
        self.selected_priority = "medium"
        
        self.priorities = [
            ("low", "🟢 Low", "#16A34A"),
            ("medium", "🟡 Medium", "#CA8A04"),
            ("high", "🟠 High", "#EA580C"),
            ("urgent", "🔴 Urgent", "#DC2626")
        ]
        
        self.buttons = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the priority picker UI"""
        for priority, label, color in self.priorities:
            btn = ctk.CTkButton(
                self,
                text=label,
                width=100,
                height=35,
                fg_color="gray30" if priority == "medium" else "transparent",
                hover_color="gray30",
                text_color=color,
                border_width=1,
                border_color=color,
                corner_radius=8,
                command=lambda p=priority: self.select_priority(p)
            )
            btn.pack(side="left", padx=5)
            self.buttons.append((priority, btn))
    
    def select_priority(self, priority: str):
        """Select a priority"""
        self.selected_priority = priority
        
        # Update button states
        for p, btn in self.buttons:
            if p == priority:
                btn.configure(fg_color="gray30")
            else:
                btn.configure(fg_color="transparent")
        
        if self.on_priority_select:
            self.on_priority_select(priority)
    
    def get_priority(self) -> str:
        """Get selected priority"""
        return self.selected_priority
    
    def set_priority(self, priority: str):
        """Set selected priority"""
        self.select_priority(priority)


class SearchBar(ctk.CTkFrame):
    """Advanced search bar with filters"""
    
    def __init__(self, parent, on_search: Callable = None, **kwargs):
        super().__init__(parent, fg_color="gray20", corner_radius=10, **kwargs)
        
        self.on_search = on_search
        self.filters = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the search bar UI"""
        # Search icon and entry
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Arial", 18)
        ).pack(side="left", padx=(5, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search notes...",
            height=35,
            border_width=0,
            fg_color="transparent",
            font=("Arial", 14)
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.do_search)
        
        # Filter button
        filter_btn = ctk.CTkButton(
            search_frame,
            text="⚙️",
            width=35,
            height=35,
            fg_color="transparent",
            hover_color="gray30",
            command=self.toggle_filters
        )
        filter_btn.pack(side="right", padx=5)
        
        # Filters frame (hidden by default)
        self.filters_frame = ctk.CTkFrame(self, fg_color="gray25", corner_radius=8)
        
        # Category filter
        ctk.CTkLabel(
            self.filters_frame,
            text="Category:",
            font=("Arial", 12)
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.category_var = ctk.StringVar(value="All")
        category_menu = ctk.CTkOptionMenu(
            self.filters_frame,
            variable=self.category_var,
            values=["All", "General", "Work", "Personal", "Ideas", "Tasks"],
            width=120,
            command=lambda v: self.update_filter("category", v)
        )
        category_menu.grid(row=0, column=1, padx=10, pady=5)
        
        # Priority filter
        ctk.CTkLabel(
            self.filters_frame,
            text="Priority:",
            font=("Arial", 12)
        ).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        self.priority_var = ctk.StringVar(value="All")
        priority_menu = ctk.CTkOptionMenu(
            self.filters_frame,
            variable=self.priority_var,
            values=["All", "low", "medium", "high", "urgent"],
            width=100,
            command=lambda v: self.update_filter("priority", v)
        )
        priority_menu.grid(row=0, column=3, padx=10, pady=5)
        
        # Starred filter
        self.starred_var = ctk.BooleanVar(value=False)
        starred_check = ctk.CTkCheckBox(
            self.filters_frame,
            text="⭐ Starred only",
            variable=self.starred_var,
            command=lambda: self.update_filter("starred", self.starred_var.get())
        )
        starred_check.grid(row=0, column=4, padx=10, pady=5)
    
    def toggle_filters(self):
        """Toggle filters visibility"""
        if self.filters_frame.winfo_ismapped():
            self.filters_frame.pack_forget()
        else:
            self.filters_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    def do_search(self, event=None):
        """Perform search"""
        search_term = self.search_entry.get().strip()
        
        if self.on_search:
            self.on_search(search_term, self.filters)
    
    def update_filter(self, filter_name: str, value):
        """Update a filter"""
        if value and value != "All":
            self.filters[filter_name] = value
        elif filter_name in self.filters:
            del self.filters[filter_name]
        
        self.do_search()
    
    def get_search_term(self) -> str:
        """Get current search term"""
        return self.search_entry.get().strip()
    
    def get_filters(self) -> dict:
        """Get current filters"""
        return self.filters.copy()
    
    def clear(self):
        """Clear search and filters"""
        self.search_entry.delete(0, "end")
        self.filters.clear()
        self.category_var.set("All")
        self.priority_var.set("All")
        self.starred_var.set(False)


class ConfirmDialog(ctk.CTkToplevel):
    """Custom confirmation dialog"""
    
    def __init__(self, parent, title: str, message: str, 
                 on_confirm: Callable = None, on_cancel: Callable = None):
        super().__init__(parent)
        
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.result = False
        
        # Configure window
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.center_window(parent)
        
        self.setup_ui(message)
    
    def center_window(self, parent):
        """Center dialog on parent"""
        self.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - 400) // 2
        y = parent_y + (parent_height - 200) // 2
        
        self.geometry(f"400x200+{x}+{y}")
    
    def setup_ui(self, message: str):
        """Setup dialog UI"""
        # Icon
        ctk.CTkLabel(
            self,
            text="⚠️",
            font=("Arial", 48)
        ).pack(pady=(30, 10))
        
        # Message
        ctk.CTkLabel(
            self,
            text=message,
            font=("Arial", 14),
            wraplength=350
        ).pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=35,
            fg_color="gray40",
            hover_color="gray50",
            command=self.cancel
        )
        cancel_btn.pack(side="left", padx=10)
        
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="Confirm",
            width=120,
            height=35,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.confirm
        )
        confirm_btn.pack(side="left", padx=10)
        
        # Bind keys
        self.bind("<Return>", lambda e: self.confirm())
        self.bind("<Escape>", lambda e: self.cancel())
    
    def confirm(self):
        """Confirm action"""
        self.result = True
        
        if self.on_confirm:
            self.on_confirm()
        
        self.destroy()
    
    def cancel(self):
        """Cancel action"""
        self.result = False
        
        if self.on_cancel:
            self.on_cancel()
        
        self.destroy()


class LoadingSpinner(ctk.CTkFrame):
    """Simple loading spinner"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.is_spinning = False
        self.angle = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup spinner UI"""
        self.label = ctk.CTkLabel(
            self,
            text="⟳",
            font=("Arial", 48)
        )
        self.label.pack()
    
    def start(self):
        """Start spinning"""
        self.is_spinning = True
        self.spin()
    
    def stop(self):
        """Stop spinning"""
        self.is_spinning = False
    
    def spin(self):
        """Animate spinner"""
        if not self.is_spinning:
            return
        
        self.angle = (self.angle + 30) % 360
        
        # Update visual (simplified - in real app would use canvas for rotation)
        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        char_index = (self.angle // 36) % len(spinner_chars)
        self.label.configure(text=spinner_chars[char_index])
        
        self.after(100, self.spin)