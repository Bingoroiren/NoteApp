import customtkinter as ctk
from datetime import datetime, timedelta
from typing import Optional
import logging

try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class AddNoteDialog(ctk.CTkToplevel):
    """Dialog tạo ghi chú - ĐÃ FIX CHỌN MÀU"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.controller = controller
        self.result = None
        self.selected_color = "#FFFFFF"  # Màu mặc định
        
        # Cấu hình window - GỌN HƠN
        self.title("Tạo ghi chú mới")
        self.geometry("580x650")
        self.minsize(500, 600)
        self.configure(fg_color="#F5F7FA")
        
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()
        
        self.title_entry.focus()
    
    def center_window(self):
        """Center dialog"""
        self.update_idletasks()
        
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        dialog_width = 580
        dialog_height = 650
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def setup_ui(self):
        """Thiết lập giao diện - TỐI ƯU"""
        # Main container với scroll
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color="#78a7bc",
            scrollbar_button_hover_color="#016191"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=18, pady=18)
        
        # Title - GỌN HƠN
        ctk.CTkLabel(
            self.scrollable_frame,
            text="Tạo ghi chú mới",
            font=("Arial", 22, "bold"),
            text_color="#016191"
        ).pack(pady=(0, 18))
        
        # Note title
        ctk.CTkLabel(
            self.scrollable_frame,
            text="Tiêu đề *",
            font=("Arial", 12, "bold"),
            anchor="w",
            text_color="#016191"
        ).pack(fill="x", pady=(8, 4))
        
        self.title_entry = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Nhập tiêu đề ghi chú...",
            height=38,
            font=("Arial", 13),
            fg_color="white",
            border_color="#78a7bc",
            text_color="#2d3748"
        )
        self.title_entry.pack(fill="x", pady=(0, 8))
        
        # Content
        ctk.CTkLabel(
            self.scrollable_frame,
            text="Nội dung",
            font=("Arial", 12, "bold"),
            anchor="w",
            text_color="#016191"
        ).pack(fill="x", pady=(8, 4))
        
        self.content_text = ctk.CTkTextbox(
            self.scrollable_frame,
            height=120,
            font=("Arial", 12),
            wrap="word",
            fg_color="white",
            border_color="#78a7bc",
            border_width=2, 
            text_color="#2d3748"
        )
        self.content_text.pack(fill="x", pady=(0, 12))
        
        # Two column layout
        meta_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        meta_frame.pack(fill="x", pady=8)
        meta_frame.grid_columnconfigure(0, weight=1)
        meta_frame.grid_columnconfigure(1, weight=1)
        
        # Category
        left_frame = ctk.CTkFrame(meta_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        ctk.CTkLabel(
            left_frame,
            text="Danh mục",
            font=("Arial", 12, "bold"),
            anchor="w",
            text_color="#016191"
        ).pack(fill="x", pady=(0, 4))
        
        self.category_var = ctk.StringVar(value="Chung")
        category_menu = ctk.CTkOptionMenu(
            left_frame,
            variable=self.category_var,
            values=["Chung", "Công việc", "Cá nhân", "Ý tưởng", "Nhiệm vụ", "Học tập", "Dự án"],
            height=32,
            font=("Arial", 11),
            fg_color="#0197ca",
            button_color="#016191",
            button_hover_color="#78a7bc",
            text_color="white"
        )
        category_menu.pack(fill="x")
        
        # Priority
        right_frame = ctk.CTkFrame(meta_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        
        ctk.CTkLabel(
            right_frame,
            text="Độ ưu tiên",
            font=("Arial", 12, "bold"),
            anchor="w",
            text_color="#016191"
        ).pack(fill="x", pady=(0, 4))
        
        self.priority_var = ctk.StringVar(value="Trung bình")
        priority_menu = ctk.CTkOptionMenu(
            right_frame,
            variable=self.priority_var,
            values=["Thấp", "Trung bình", "Cao", "Khẩn cấp"],
            height=32,
            font=("Arial", 11),
            fg_color="#0197ca",
            button_color="#016191",
            button_hover_color="#78a7bc",
            text_color="white"
        )
        priority_menu.pack(fill="x")
        
        # Tags
        ctk.CTkLabel(
            self.scrollable_frame,
            text="Thẻ",
            font=("Arial", 12, "bold"),
            anchor="w",
            text_color="#016191"
        ).pack(fill="x", pady=(12, 4))
        
        self.tags_entry = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Nhập thẻ phân cách bằng dấu phẩy",
            height=32,
            font=("Arial", 11),
            fg_color="white",
            border_color="#78a7bc",
            text_color="#2d3748"
        )
        self.tags_entry.pack(fill="x", pady=(0, 12))
        
        # === PHẦN NGÀY ĐẾN HẠN VÀ NHẮC NHỞ - THAY THẾ MÀU SẮC ===
        due_reminder_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white", corner_radius=8)
        due_reminder_frame.pack(fill="x", pady=12, padx=2)

        # Container chính
        due_reminder_container = ctk.CTkFrame(due_reminder_frame, fg_color="transparent")
        due_reminder_container.pack(fill="x", padx=12, pady=10)

        # Ngày đến hạn
        due_date_frame = ctk.CTkFrame(due_reminder_container, fg_color="transparent")
        due_date_frame.pack(fill="x", pady=5)

      
        self.due_date_btn = ctk.CTkButton(
            due_date_frame,
            text="Ngày đến hạn",
            width=70,
            height=28,
            font=("Arial", 10),
            fg_color="#0197ca",
            hover_color="#016191",
            text_color="white",
            command=self.toggle_due_date
        )
        self.due_date_btn.pack(side="left", padx=(0, 10))
        self.due_date_frame = ctk.CTkFrame(due_date_frame, fg_color="#e8f4f8", corner_radius=6)

        if TKCALENDAR_AVAILABLE:
            from tkcalendar import DateEntry
            
            self.due_date_entry = DateEntry(
                self.due_date_frame,
                width=12,
                background='#016191',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy',
                mindate=datetime.now().date(),
                font=("Arial", 10)
            )
            self.due_date_entry.pack(side="left", padx=12, pady=8)
        else:
            self.due_date_entry = ctk.CTkEntry(
                self.due_date_frame,
                placeholder_text="DD/MM/YYYY",
                width=120,
                height=30,
                font=("Arial", 11),
                fg_color="white",
                border_color="#78a7bc",
                text_color="#2d3748"
            )
            self.due_date_entry.pack(side="left", padx=12, pady=8)
            self.due_date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Nút ngày nhanh
        quick_dates_frame = ctk.CTkFrame(self.due_date_frame, fg_color="transparent")
        quick_dates_frame.pack(side="left", padx=10, pady=8)

        quick_buttons = [
            ("Hôm nay", 0),
            ("Ngày mai", 1),
            ("Tuần sau", 7)
        ]

        for text, days in quick_buttons:
            btn = ctk.CTkButton(
                quick_dates_frame,
                text=text,
                width=70,
                height=26,
                font=("Arial", 10),
                command=lambda d=days: self.set_quick_date(d),
                fg_color="#0197ca",
                hover_color="#016191",
                text_color="white"
            )
            btn.pack(side="left", padx=2)

        # Thời gian nhắc nhở
        reminder_frame = ctk.CTkFrame(due_reminder_container, fg_color="transparent")
        reminder_frame.pack(fill="x", pady=5)

        self.reminder_btn = ctk.CTkButton(
            reminder_frame,
            text="Nhắc nhở",
            width=70,
            height=28,
            font=("Arial", 10),
            fg_color="#0197ca",
            hover_color="#016191",
            text_color="white",
            command=self.toggle_reminder
        )
        self.reminder_btn.pack(side="left", padx=(0, 10))

        self.reminder_frame = ctk.CTkFrame(reminder_frame, fg_color="#e8f4f8", corner_radius=6)

        # Container chứa giờ và lặp lại trên cùng 1 hàng
        time_recurring_container = ctk.CTkFrame(self.reminder_frame, fg_color="transparent")
        time_recurring_container.pack(fill="x", padx=12, pady=8)

        # Phần bên trái - Thời gian nhắc nhở
        time_frame = ctk.CTkFrame(time_recurring_container, fg_color="transparent")
        time_frame.pack(side="left")

        ctk.CTkLabel(
            time_frame, 
            text="Giờ:", 
            font=("Arial", 11), 
            text_color="#016191"
        ).pack(side="left", padx=(0, 5))

        self.reminder_hour = ctk.CTkEntry(
            time_frame, 
            width=45, 
            placeholder_text="HH",
            font=("Arial", 11),
            fg_color="white",
            border_color="#78a7bc",
            text_color="#2d3748"
        )
        self.reminder_hour.pack(side="left", padx=2)
        self.reminder_hour.insert(0, "09")  # Giờ mặc định

        ctk.CTkLabel(
            time_frame, 
            text=":", 
            font=("Arial", 11), 
            text_color="#016191"
        ).pack(side="left")

        self.reminder_minute = ctk.CTkEntry(
            time_frame, 
            width=45, 
            placeholder_text="MM",
            font=("Arial", 11),
            fg_color="white",
            border_color="#78a7bc",
            text_color="#2d3748"
        )
        self.reminder_minute.pack(side="left", padx=2)
        self.reminder_minute.insert(0, "00")  # Phút mặc định

        # Phần bên phải - Tùy chọn lặp lại
        recurring_frame = ctk.CTkFrame(time_recurring_container, fg_color="transparent")
        recurring_frame.pack(side="right")

        ctk.CTkLabel(
            recurring_frame,
            text="Lặp lại:",
            font=("Arial", 11),
            text_color="#016191"
        ).pack(side="left", padx=(0, 8))

        self.recurring_var = ctk.StringVar(value="Không")
        recurring_menu = ctk.CTkOptionMenu(
            recurring_frame,
            variable=self.recurring_var,
            values=["Không", "Hàng ngày", "Hàng tuần", "Hàng tháng"],
            width=100,
            height=28,
            font=("Arial", 10),
            fg_color="#0197ca",
            button_color="#016191",
            button_hover_color="#78a7bc",
            text_color="white"
        )
        recurring_menu.pack(side="left")
        # Buttons - Đặt ở ngoài scrollable frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=18, pady=(0, 15))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Hủy",
            width=110,
            height=38,
            font=("Arial", 12),
            fg_color="#d4dada",
            hover_color="#adcace",
            text_color="#2d3748",
            command=self.cancel
        )
        cancel_btn.pack(side="right", padx=(8, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Tạo ghi chú",
            width=110,
            height=38,
            font=("Arial", 12, "bold"),
            fg_color="#0197ca",
            hover_color="#016191",
            text_color="white",
            command=self.save
        )
        save_btn.pack(side="right")
        
        # Bind keys
        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.cancel())
    
    def set_color(self, color: str):
        """Thiết lập màu - ĐÃ FIX"""
        self.selected_color = color
        self.color_var.set(color)
        self.highlight_selected_color(color)
        logger.info(f"Đã chọn màu: {color}")
    
    def highlight_selected_color(self, selected_color: str):
        """Highlight nút màu đã chọn - TÍNH NĂNG MỚI"""
        for color, btn in self.color_buttons:
            if color == selected_color:
                # Border dày hơn cho màu đã chọn
                btn.configure(border_width=3, border_color="#016191")
            else:
                # Border bình thường
                btn.configure(border_width=2, border_color="#78a7bc")
    
    def validate_inputs(self) -> bool:
        """Validate form inputs"""
        title = self.title_entry.get().strip()
        if not title:
            self.show_error("Tiêu đề là bắt buộc")
            return False
        
        return True
    
    def save(self):
        """Lưu ghi chú - ĐÃ THÊM NGÀY ĐẾN HẠN VÀ NHẮC NHỞ"""
        if not self.validate_inputs():
            return
        
        try:
            title = self.title_entry.get().strip()
            content = self.content_text.get("1.0", "end-1c").strip()
            
            # Chuyển đổi danh mục và độ ưu tiên
            category_map = {
                "Chung": "General",
                "Công việc": "Work", 
                "Cá nhân": "Personal",
                "Ý tưởng": "Ideas",
                "Nhiệm vụ": "Tasks",
                "Học tập": "Study",
                "Dự án": "Projects"
            }
            priority_map = {
                "Thấp": "low",
                "Trung bình": "medium", 
                "Cao": "high",
                "Khẩn cấp": "urgent"
            }
            
            category = category_map.get(self.category_var.get(), "General")
            priority = priority_map.get(self.priority_var.get(), "medium")
            
            tags_text = self.tags_entry.get().strip()
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            
            # Xử lý ngày đến hạn
            due_date = None
            if self.due_date_frame.winfo_ismapped():
                if TKCALENDAR_AVAILABLE:
                    try:
                        due_date = self.due_date_entry.get_date()
                        due_date = datetime.combine(due_date, datetime.min.time())
                    except:
                        date_str = self.due_date_entry.get()
                        if date_str:
                            try:
                                due_date = datetime.strptime(date_str, "%d/%m/%Y")
                            except:
                                pass
                else:
                    date_str = self.due_date_entry.get()
                    if date_str:
                        try:
                            due_date = datetime.strptime(date_str, "%d/%m/%Y")
                        except:
                            pass
            
            # Xử lý nhắc nhở
            reminders = []
            if self.reminder_frame.winfo_ismapped():
                try:
                    hour = int(self.reminder_hour.get())
                    minute = int(self.reminder_minute.get())
                    
                    if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                        raise ValueError("Thời gian không hợp lệ")
                    
                    # Tạo thời gian nhắc nhở
                    reminder_date = due_date if due_date else datetime.now()
                    reminder_time = reminder_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Nếu thời gian đã qua, đặt cho ngày mai
                    if reminder_time <= datetime.now():
                        reminder_time += timedelta(days=1)
                    
                    # Xử lý lặp lại
                    recurring_map = {
                        "Không": None,
                        "Hàng ngày": "daily",
                        "Hàng tuần": "weekly", 
                        "Hàng tháng": "monthly"
                    }
                    recurring = recurring_map.get(self.recurring_var.get(), None)
                    
                    reminder = {
                        'time': reminder_time,
                        'recurring': recurring,
                        'snoozed_until': None
                    }
                    reminders.append(reminder)
                    
                except ValueError as e:
                    self.show_error("Thời gian nhắc nhở không hợp lệ (HH:MM)")
                    return
            
            # Tạo ghi chú
            note_id = self.controller.create_note(
                title=title,
                content=content,
                category=category,
                tags=tags,
                priority=priority,
                due_date=due_date,
                reminders=reminders,
                color_code="#FFFFFF"  # Màu mặc định
            )
            
            if note_id:
                logger.info(f"Note created with due_date and reminders: {note_id}")
                self.result = note_id
                self.destroy()
            else:
                self.show_error("Không thể tạo ghi chú")
        
        except Exception as e:
            logger.error(f"Error creating note: {str(e)}")
            self.show_error(f"Lỗi: {str(e)}")
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.destroy()
    
    def toggle_due_date(self):
        """Toggle hiển thị ngày đến hạn"""
        if self.due_date_frame.winfo_ismapped():
            self.due_date_frame.pack_forget()
            self.due_date_btn.configure(text="Ngày đến hạn", fg_color="#0197ca")
        else:
            self.due_date_frame.pack(side="left", padx=(10, 0), pady=0)
            self.due_date_btn.configure(text="Ngày đến hạn", fg_color="#16A34A")

    def toggle_reminder(self):
        """Toggle hiển thị nhắc nhở"""
        if self.reminder_frame.winfo_ismapped():
            self.reminder_frame.pack_forget()
            self.reminder_btn.configure(text="Nhắc nhở", fg_color="#0197ca")
        else:
            self.reminder_frame.pack(side="left", padx=(10, 0), pady=0)
            self.reminder_btn.configure(text="Nhắc nhở", fg_color="#16A34A")
    def set_quick_date(self, days: int):
        """Đặt ngày nhanh"""
        target_date = datetime.now() + timedelta(days=days)
        
        if TKCALENDAR_AVAILABLE:
            try:
                self.due_date_entry.set_date(target_date.date())
            except:
                self.due_date_entry.delete(0, "end")
                self.due_date_entry.insert(0, target_date.strftime("%d/%m/%Y"))
        else:
            self.due_date_entry.delete(0, "end")
            self.due_date_entry.insert(0, target_date.strftime("%d/%m/%Y"))
    def show_error(self, message: str):
        """Show error message - GỌN HƠN"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Lỗi")
        error_dialog.geometry("350x150")
        error_dialog.transient(self)
        error_dialog.grab_set()
        error_dialog.configure(fg_color="#F5F7FA")
        
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        error_dialog.geometry(f"350x150+{x}+{y}")
        
        ctk.CTkLabel(
            error_dialog,
            text="⚠️",
            font=("Arial", 35)
        ).pack(pady=(18, 8))
        
        ctk.CTkLabel(
            error_dialog,
            text=message,
            font=("Arial", 12),
            text_color="#2d3748"
        ).pack(pady=8)
        
        ctk.CTkButton(
            error_dialog,
            text="Đóng",
            width=90,
            fg_color="#0197ca",
            hover_color="#016191",
            text_color="white",
            command=error_dialog.destroy
        ).pack(pady=10)