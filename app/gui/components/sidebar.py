"""
Sidebar component for navigation and filtering
"""
import customtkinter as ctk
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class Sidebar(ctk.CTkFrame):
    """Sidebar navigation component"""
    
    def __init__(self, parent, on_filter_callback: Callable):
        super().__init__(parent, width=280, corner_radius=0)
        
        self.on_filter_callback = on_filter_callback
        self.current_filter = "all"
        
        # Prevent frame from shrinking
        self.grid_propagate(False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the sidebar UI"""
        # App title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            title_frame,
            text="📝 NoteApp",
            font=("Arial", 24, "bold")
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Advanced Note Taking",
            font=("Arial", 11),
            text_color="gray"
        )
        subtitle.pack(anchor="w")
        
        # Separator
        ctk.CTkFrame(self, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=10)
        
        # Main filters
        self.create_section("QUICK ACCESS")
        
        self.btn_all = self.create_nav_button(
            "📋 All Notes",
            lambda: self.set_filter("all"),
            active=True
        )
        
        self.btn_starred = self.create_nav_button(
            "⭐ Starred",
            lambda: self.set_filter("starred")
        )
        
        self.btn_archived = self.create_nav_button(
            "📦 Archived",
            lambda: self.set_filter("archived")
        )
        
        # Priority filters
        self.create_section("PRIORITY")
        
        self.btn_urgent = self.create_nav_button(
            "🔴 Urgent",
            lambda: self.set_filter("priority:urgent"),
            color="#DC2626"
        )
        
        self.btn_high = self.create_nav_button(
            "🟠 High",
            lambda: self.set_filter("priority:high"),
            color="#EA580C"
        )
        
        self.btn_medium = self.create_nav_button(
            "🟡 Medium",
            lambda: self.set_filter("priority:medium"),
            color="#CA8A04"
        )
        
        self.btn_low = self.create_nav_button(
            "🟢 Low",
            lambda: self.set_filter("priority:low"),
            color="#16A34A"
        )
        
        # Categories (will be populated dynamically)
        self.create_section("CATEGORIES")
        self.categories_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.categories_frame.pack(fill="x", padx=10, pady=5)
        
        # Statistics
        self.create_section("STATISTICS")
        self.stats_frame = ctk.CTkFrame(self, fg_color="gray20", corner_radius=10)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_labels = {}
        self.create_stat_row("Total Notes", "0")
        self.create_stat_row("Starred", "0")
        self.create_stat_row("This Week", "0")
        
        # Spacer
        ctk.CTkFrame(self, fg_color="transparent").pack(fill="both", expand=True)
        
        # Settings button at bottom
        settings_btn = ctk.CTkButton(
            self,
            text="⚙️ Settings",
            font=("Arial", 13),
            fg_color="transparent",
            hover_color="gray30",
            anchor="w",
            command=self.show_settings
        )
        settings_btn.pack(fill="x", padx=20, pady=(10, 20))
    
    def create_section(self, title: str):
        """Create a section header"""
        label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 11, "bold"),
            text_color="gray50",
            anchor="w"
        )
        label.pack(fill="x", padx=20, pady=(15, 5))
    
    def create_nav_button(self, text: str, command: Callable, 
                         active: bool = False, color: str = None) -> ctk.CTkButton:
        """Create a navigation button"""
        btn = ctk.CTkButton(
            self,
            text=text,
            font=("Arial", 13),
            fg_color="gray30" if active else "transparent",
            hover_color="gray30",
            anchor="w",
            height=40,
            corner_radius=8,
            command=command
        )
        
        if color:
            btn.configure(text_color=color)
        
        btn.pack(fill="x", padx=20, pady=2)
        return btn
    
    def create_stat_row(self, label: str, value: str):
        """Create a statistics row"""
        row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=5)
        
        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=("Arial", 12),
            anchor="w"
        )
        label_widget.pack(side="left")
        
        value_widget = ctk.CTkLabel(
            row,
            text=value,
            font=("Arial", 12, "bold"),
            anchor="e"
        )
        value_widget.pack(side="right")
        
        self.stats_labels[label] = value_widget
    
    def set_filter(self, filter_type: str):
        """Set the current filter and update UI"""
        self.current_filter = filter_type
        
        # Reset all button colors
        for btn in [self.btn_all, self.btn_starred, self.btn_archived,
                   self.btn_urgent, self.btn_high, self.btn_medium, self.btn_low]:
            btn.configure(fg_color="transparent")
        
        # Highlight active button
        if filter_type == "all":
            self.btn_all.configure(fg_color="gray30")
        elif filter_type == "starred":
            self.btn_starred.configure(fg_color="gray30")
        elif filter_type == "archived":
            self.btn_archived.configure(fg_color="gray30")
        elif filter_type == "priority:urgent":
            self.btn_urgent.configure(fg_color="gray30")
        elif filter_type == "priority:high":
            self.btn_high.configure(fg_color="gray30")
        elif filter_type == "priority:medium":
            self.btn_medium.configure(fg_color="gray30")
        elif filter_type == "priority:low":
            self.btn_low.configure(fg_color="gray30")
        
        # Trigger callback
        if self.on_filter_callback:
            self.on_filter_callback(filter_type)
    
    def update_categories(self, categories: list):
        """Update the categories list"""
        # Clear existing
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        # Add category buttons
        for category in categories[:5]:  # Show max 5 categories
            btn = ctk.CTkButton(
                self.categories_frame,
                text=f"📁 {category}",
                font=("Arial", 12),
                fg_color="transparent",
                hover_color="gray30",
                anchor="w",
                height=35,
                command=lambda c=category: self.set_filter(f"category:{c}")
            )
            btn.pack(fill="x", pady=2)
        
        if len(categories) > 5:
            more_btn = ctk.CTkButton(
                self.categories_frame,
                text=f"+ {len(categories) - 5} more...",
                font=("Arial", 11),
                fg_color="transparent",
                text_color="gray50",
                hover_color="gray30",
                anchor="w",
                height=30,
                command=self.show_all_categories
            )
            more_btn.pack(fill="x", pady=2)
    
    def update_stats(self, stats: dict):
        """Update statistics"""
        if "total_notes" in stats:
            self.stats_labels["Total Notes"].configure(text=str(stats["total_notes"]))
        
        if "starred" in stats:
            self.stats_labels["Starred"].configure(text=str(stats["starred"]))
        
        if "due_this_week" in stats:
            self.stats_labels["This Week"].configure(text=str(stats["due_this_week"]))
    
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        logger.info("Settings clicked")
    
    def show_all_categories(self):
        """Show all categories dialog"""
        # TODO: Implement categories dialog
        logger.info("Show all categories clicked")