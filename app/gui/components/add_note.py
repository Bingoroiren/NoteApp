"""
Add note dialog component
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from typing import Optional
import logging

# Try to import tkcalendar, fallback to standard entry if not available
try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False
    print("Warning: tkcalendar not installed. Using basic date entry. Install with: pip install tkcalendar")

logger = logging.getLogger(__name__)


class AddNoteDialog(ctk.CTkToplevel):
    """Dialog for creating a new note"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.controller = controller
        self.result = None
        
        # Configure window
        self.title("Create New Note")
        self.geometry("600x700")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.center_window()
        
        self.setup_ui()
        
        # Focus on title
        self.title_entry.focus()
    
    def center_window(self):
        """Center the dialog on parent window"""
        self.update_idletasks()
        
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        dialog_width = 600
        dialog_height = 700
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="✍️ Create New Note",
            font=("Arial", 24, "bold")
        ).pack(pady=(0, 20))
        
        # Note title
        ctk.CTkLabel(
            main_frame,
            text="Title *",
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.title_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter note title...",
            height=40,
            font=("Arial", 14)
        )
        self.title_entry.pack(fill="x")
        
        # Content
        ctk.CTkLabel(
            main_frame,
            text="Content",
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(15, 5))
        
        self.content_text = ctk.CTkTextbox(
            main_frame,
            height=150,
            font=("Arial", 13),
            wrap="word"
        )
        self.content_text.pack(fill="x")
        
        # Two column layout for metadata
        meta_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        meta_frame.pack(fill="x", pady=15)
        meta_frame.grid_columnconfigure(0, weight=1)
        meta_frame.grid_columnconfigure(1, weight=1)
        
        # Category
        left_frame = ctk.CTkFrame(meta_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ctk.CTkLabel(
            left_frame,
            text="📁 Category",
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.category_var = ctk.StringVar(value="General")
        category_menu = ctk.CTkOptionMenu(
            left_frame,
            variable=self.category_var,
            values=["General", "Work", "Personal", "Ideas", "Tasks", "Study", "Projects"],
            height=35
        )
        category_menu.pack(fill="x")
        
        # Priority
        right_frame = ctk.CTkFrame(meta_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        ctk.CTkLabel(
            right_frame,
            text="🎯 Priority",
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.priority_var = ctk.StringVar(value="medium")
        priority_menu = ctk.CTkOptionMenu(
            right_frame,
            variable=self.priority_var,
            values=["low", "medium", "high", "urgent"],
            height=35
        )
        priority_menu.pack(fill="x")
        
        # Tags
        ctk.CTkLabel(
            main_frame,
            text="🏷️ Tags",
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(15, 5))
        
        self.tags_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter tags separated by comma (e.g., work, important, meeting)",
            height=35
        )
        self.tags_entry.pack(fill="x")
        
        # Due date
        due_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        due_frame.pack(fill="x", pady=15)
        
        self.due_date_enabled = ctk.BooleanVar(value=False)
        due_checkbox = ctk.CTkCheckBox(
            due_frame,
            text="⏰ Set Due Date",
            variable=self.due_date_enabled,
            font=("Arial", 13, "bold"),
            command=self.toggle_due_date
        )
        due_checkbox.pack(anchor="w", pady=(0, 5))
        
        self.due_date_frame = ctk.CTkFrame(due_frame, fg_color="gray20", corner_radius=8)
        
        if TKCALENDAR_AVAILABLE:
            from tkcalendar import DateEntry
            
            self.due_date_entry = DateEntry(
                self.due_date_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd',
                mindate=datetime.now().date()
            )
            self.due_date_entry.pack(side="left", padx=15, pady=10)
        else:
            # Fallback: Simple entry with placeholder
            self.due_date_entry = ctk.CTkEntry(
                self.due_date_frame,
                placeholder_text="YYYY-MM-DD",
                width=150
            )
            self.due_date_entry.pack(side="left", padx=15, pady=10)
            
            # Add today's date as default
            self.due_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Quick due date buttons
        quick_dates_frame = ctk.CTkFrame(self.due_date_frame, fg_color="transparent")
        quick_dates_frame.pack(side="left", padx=10, pady=10)
        
        quick_buttons = [
            ("Today", 0),
            ("Tomorrow", 1),
            ("Next Week", 7),
            ("Next Month", 30)
        ]
        
        for text, days in quick_buttons:
            btn = ctk.CTkButton(
                quick_dates_frame,
                text=text,
                width=80,
                height=25,
                font=("Arial", 11),
                command=lambda d=days: self.set_quick_date(d)
            )
            btn.pack(side="left", padx=2)
        
        # Reminder
        reminder_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        reminder_frame.pack(fill="x", pady=15)
        
        self.reminder_enabled = ctk.BooleanVar(value=False)
        reminder_checkbox = ctk.CTkCheckBox(
            reminder_frame,
            text="🔔 Set Reminder",
            variable=self.reminder_enabled,
            font=("Arial", 13, "bold"),
            command=self.toggle_reminder
        )
        reminder_checkbox.pack(anchor="w", pady=(0, 5))
        
        self.reminder_frame = ctk.CTkFrame(reminder_frame, fg_color="gray20", corner_radius=8)
        
        # Reminder time inputs
        time_frame = ctk.CTkFrame(self.reminder_frame, fg_color="transparent")
        time_frame.pack(padx=15, pady=10)
        
        ctk.CTkLabel(time_frame, text="Time:").pack(side="left", padx=(0, 5))
        
        self.reminder_hour = ctk.CTkEntry(time_frame, width=50, placeholder_text="HH")
        self.reminder_hour.pack(side="left", padx=2)
        
        ctk.CTkLabel(time_frame, text=":").pack(side="left")
        
        self.reminder_minute = ctk.CTkEntry(time_frame, width=50, placeholder_text="MM")
        self.reminder_minute.pack(side="left", padx=2)
        
        # Recurring option
        self.recurring_var = ctk.StringVar(value="none")
        recurring_menu = ctk.CTkOptionMenu(
            self.reminder_frame,
            variable=self.recurring_var,
            values=["none", "daily", "weekly", "monthly"],
            width=120
        )
        recurring_menu.pack(padx=15, pady=(0, 10))
        
        # Color picker
        color_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        color_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            color_frame,
            text="🎨 Color",
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=(0, 10))
        
        self.color_var = ctk.StringVar(value="#FFFFFF")
        colors = [
            ("#FFFFFF", "White"),
            ("#FEF3C7", "Yellow"),
            ("#DBEAFE", "Blue"),
            ("#D1FAE5", "Green"),
            ("#FCE7F3", "Pink"),
            ("#F3E8FF", "Purple")
        ]
        
        for color, name in colors:
            btn = ctk.CTkButton(
                color_frame,
                text="",
                width=40,
                height=30,
                fg_color=color,
                hover_color=color,
                border_width=2,
                border_color="gray40",
                command=lambda c=color: self.set_color(c)
            )
            btn.pack(side="left", padx=2)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=40,
            fg_color="gray40",
            hover_color="gray50",
            command=self.cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Create Note",
            width=120,
            height=40,
            command=self.save
        )
        save_btn.pack(side="right")
        
        # Bind Enter key
        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.cancel())
    
    def toggle_due_date(self):
        """Toggle due date frame visibility"""
        if self.due_date_enabled.get():
            self.due_date_frame.pack(fill="x", pady=(5, 0))
        else:
            self.due_date_frame.pack_forget()
    
    def toggle_reminder(self):
        """Toggle reminder frame visibility"""
        if self.reminder_enabled.get():
            self.reminder_frame.pack(fill="x", pady=(5, 0))
        else:
            self.reminder_frame.pack_forget()
    
    def set_quick_date(self, days: int):
        """Set due date using quick button"""
        target_date = datetime.now() + timedelta(days=days)
        
        if TKCALENDAR_AVAILABLE:
            try:
                from tkcalendar import DateEntry
                self.due_date_entry.set_date(target_date.date())
            except:
                self.due_date_entry.delete(0, "end")
                self.due_date_entry.insert(0, target_date.strftime("%Y-%m-%d"))
        else:
            self.due_date_entry.delete(0, "end")
            self.due_date_entry.insert(0, target_date.strftime("%Y-%m-%d"))
    
    def set_color(self, color: str):
        """Set note color"""
        self.color_var.set(color)
    
    def validate_inputs(self) -> bool:
        """Validate form inputs"""
        # Title is required
        title = self.title_entry.get().strip()
        if not title:
            self.show_error("Title is required")
            return False
        
        # Validate reminder time if enabled
        if self.reminder_enabled.get():
            try:
                hour = int(self.reminder_hour.get())
                minute = int(self.reminder_minute.get())
                
                if not (0 <= hour <= 23):
                    self.show_error("Hour must be between 0 and 23")
                    return False
                
                if not (0 <= minute <= 59):
                    self.show_error("Minute must be between 0 and 59")
                    return False
            except ValueError:
                self.show_error("Invalid time format")
                return False
        
        return True
    
    def save(self):
        """Save the new note"""
        if not self.validate_inputs():
            return
        
        try:
            # Collect form data
            title = self.title_entry.get().strip()
            content = self.content_text.get("1.0", "end-1c").strip()
            category = self.category_var.get()
            priority = self.priority_var.get()
            color = self.color_var.get()
            
            # Parse tags
            tags_text = self.tags_entry.get().strip()
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            
            # Parse due date
            due_date = None
            if self.due_date_enabled.get():
                if TKCALENDAR_AVAILABLE:
                    try:
                        from tkcalendar import DateEntry
                        due_date = self.due_date_entry.get_date()
                        due_date = datetime.combine(due_date, datetime.min.time())
                    except:
                        date_str = self.due_date_entry.get()
                        if date_str:
                            try:
                                due_date = datetime.strptime(date_str, "%Y-%m-%d")
                            except:
                                pass
                else:
                    date_str = self.due_date_entry.get()
                    if date_str:
                        try:
                            due_date = datetime.strptime(date_str, "%Y-%m-%d")
                        except:
                            pass
            
            # Parse reminder
            reminders = []
            if self.reminder_enabled.get():
                hour = int(self.reminder_hour.get())
                minute = int(self.reminder_minute.get())
                
                # Use due date or today
                reminder_date = due_date if due_date else datetime.now()
                reminder_time = reminder_date.replace(hour=hour, minute=minute, second=0)
                
                # Ensure reminder is in the future
                if reminder_time <= datetime.now():
                    reminder_time += timedelta(days=1)
                
                recurring = self.recurring_var.get()
                if recurring == "none":
                    recurring = None
                
                reminders.append({
                    'time': reminder_time,
                    'recurring': recurring,
                    'snoozed_until': None
                })
            
            # Create note
            note_id = self.controller.create_note(
                title=title,
                content=content,
                category=category,
                tags=tags,
                priority=priority,
                due_date=due_date,
                reminders=reminders,
                color_code=color
            )
            
            if note_id:
                logger.info(f"Note created: {note_id}")
                self.result = note_id
                self.destroy()
            else:
                self.show_error("Failed to create note")
        
        except Exception as e:
            logger.error(f"Error creating note: {str(e)}")
            self.show_error(f"Error: {str(e)}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.destroy()
    
    def show_error(self, message: str):
        """Show error message"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("400x150")
        error_dialog.transient(self)
        error_dialog.grab_set()
        
        # Center on this dialog
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        error_dialog.geometry(f"400x150+{x}+{y}")
        
        ctk.CTkLabel(
            error_dialog,
            text="❌",
            font=("Arial", 40)
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            error_dialog,
            text=message,
            font=("Arial", 13)
        ).pack(pady=10)
        
        ctk.CTkButton(
            error_dialog,
            text="OK",
            width=100,
            command=error_dialog.destroy
        ).pack(pady=10)