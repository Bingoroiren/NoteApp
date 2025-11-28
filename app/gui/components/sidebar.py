import customtkinter as ctk
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class Sidebar(ctk.CTkFrame):
    
    def __init__(self, parent, on_filter_callback: Callable, on_sort_callback: Callable):
        super().__init__(parent, width=280, corner_radius=0, fg_color="#e8f4f8")
        
        self.on_filter_callback = on_filter_callback
        self.on_sort_callback = on_sort_callback
        self.current_filter = "all"
        self.sort_by = "created_date"
        self.sort_ascending = False
        
        self.grid_propagate(False)
        self.setup_ui()
    
    def setup_ui(self):
        # Main container với scroll
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#78a7bc",
            scrollbar_button_hover_color="#016191"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        title_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=18, pady=15)
        
        title = ctk.CTkLabel(
            title_frame,
            text="NoteApp",
            font=("Arial", 22, "bold"),
            text_color="#016191"
        )
        title.pack(anchor="w")
        
        # Separator
        ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="#adcace").pack(fill="x", padx=18, pady=8)
        
        #   PHẦN SẮP XẾP  
        self.create_section("SẮP XẾP")
        
        sort_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white", corner_radius=8)
        sort_frame.pack(fill="x", padx=18, pady=5)
        clear_sort_frame = ctk.CTkFrame(sort_frame, fg_color="transparent")
        clear_sort_frame.pack(fill="x", padx=10, pady=5)
        self.btn_clear_sort = ctk.CTkButton(
            clear_sort_frame,
            text="Bỏ sắp xếp",
            width=100,
            height=28,
            font=("Arial", 10),
            fg_color="transparent",
            hover_color="#d4dada",
            text_color="#78a7bc",
            border_width=1,
            border_color="#adcace",
            command=self.clear_sort
        )
        self.btn_clear_sort.pack(side="right", padx=2)
        # Sắp xếp theo ngày tạo
        date_frame = ctk.CTkFrame(sort_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            date_frame,
            text="Ngày tạo:",
            font=("Arial", 11),
            text_color="#2d3748"
        ).pack(side="left")

        self.btn_date = ctk.CTkButton(
            date_frame,
            text="Mới nhất",  # Mặc định
            width=80,
            height=28,
            font=("Arial", 10),
            fg_color="transparent",
            hover_color="#d4dada",
            text_color="#016191",
            border_width=1,
            border_color="#adcace",
            command=lambda: self.toggle_sort("created_date")
        )
        self.btn_date.pack(side="right", padx=2)
        # Sắp xếp theo độ ưu tiên
        priority_frame = ctk.CTkFrame(sort_frame, fg_color="transparent")
        priority_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            priority_frame,
            text="Ưu tiên:",
            font=("Arial", 11),
            text_color="#2d3748"
        ).pack(side="left")

        self.btn_priority = ctk.CTkButton(
            priority_frame,
            text="Cao→Thấp",  # Mặc định
            width=80,
            height=28,
            font=("Arial", 10),
            fg_color="transparent",
            hover_color="#d4dada",
            text_color="#016191",
            border_width=1,
            border_color="#adcace",
            command=lambda: self.toggle_sort("priority")
        )
        self.btn_priority.pack(side="right", padx=2)
        # Sắp xếp theo tên
        title_frame = ctk.CTkFrame(sort_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            title_frame,
            text="Tiêu đề:",
            font=("Arial", 11),
            text_color="#2d3748"
        ).pack(side="left")

        self.btn_title = ctk.CTkButton(
            title_frame,
            text="A→Z",  # Mặc định
            width=80,
            height=28,
            font=("Arial", 10),
            fg_color="transparent",
            hover_color="#d4dada",
            text_color="#016191",
            border_width=1,
            border_color="#adcace",
            command=lambda: self.toggle_sort("title")
        )
        self.btn_title.pack(side="right", padx=2)
        # Main filters
        self.create_section("TRUY CẬP NHANH")
        
        self.btn_all = self.create_nav_button(
            "Tất cả ghi chú",
            lambda: self.set_filter("all"),
            active=True
        )
        
        self.btn_starred = self.create_nav_button(
            "Quan trọng",
            lambda: self.set_filter("starred")
        )
        
        self.btn_archived = self.create_nav_button(
            "Lưu trữ",
            lambda: self.set_filter("archived")
        )
        
        # Priority filters
        self.create_section("ĐỘ ƯU TIÊN")
        
        self.btn_urgent = self.create_nav_button(
            "Khẩn cấp",
            lambda: self.set_filter("priority:urgent"),
            color="#DC2626"
        )
        
        self.btn_high = self.create_nav_button(
            "Cao",
            lambda: self.set_filter("priority:high"),
            color="#EA580C"
        )
        
        self.btn_medium = self.create_nav_button(
            "Trung bình",
            lambda: self.set_filter("priority:medium"),
            color="#CA8A04"
        )
        
        self.btn_low = self.create_nav_button(
            "Thấp",
            lambda: self.set_filter("priority:low"),
            color="#16A34A"
        )
        
        # Categories
        self.create_section("DANH MỤC")
        self.categories_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.categories_frame.pack(fill="x", padx=10, pady=5)
        
        # Danh mục mặc định
        default_categories = ["Chung", "Công việc", "Cá nhân", "Ý tưởng", "Nhiệm vụ"]
        for cat in default_categories:
            self.create_category_button(cat)
        
        # Statistics
        self.create_section("THỐNG KÊ")
        self.stats_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white", corner_radius=8)
        self.stats_frame.pack(fill="x", padx=18, pady=8)
        
        self.stats_labels = {}
        self.create_stat_row("Tổng số", "0")
        self.create_stat_row("Quan trọng", "0")
        self.create_stat_row("Tuần này", "0")
        self.update_sort_buttons()
        # Thêm padding ở cuối để đảm bảo nội dung không bị che
        ctk.CTkFrame(self.scrollable_frame, height=10, fg_color="transparent").pack()
    
    def create_section(self, title: str):
        label = ctk.CTkLabel(
            self.scrollable_frame,
            text=title,
            font=("Arial", 10, "bold"),
            text_color="#78a7bc",
            anchor="w"
        )
        label.pack(fill="x", padx=18, pady=(12, 4))
    
    def create_nav_button(self, text: str, command: Callable, 
                         active: bool = False, color: str = None) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            self.scrollable_frame,
            text=text,
            font=("Arial", 12),
            fg_color="#0197ca" if active else "transparent",
            hover_color="#d4dada",
            anchor="w",
            height=36,
            corner_radius=6,
            text_color=color if color else ("#FFFFFF" if active else "#016191"),
            command=command
        )
        
        btn.pack(fill="x", padx=18, pady=2)
        return btn
    
    def create_category_button(self, category: str):
        # Map tên tiếng Việt sang tiếng Anh
        cat_map = {
            "Chung": "General",
            "Công việc": "Work",
            "Cá nhân": "Personal",
            "Ý tưởng": "Ideas",
            "Nhiệm vụ": "Tasks"
        }
        
        cat_en = cat_map.get(category, category)
        
        btn = ctk.CTkButton(
            self.categories_frame,
            text=category,
            font=("Arial", 11),
            fg_color="transparent",
            hover_color="#d4dada",
            anchor="w",
            height=32,
            text_color="#016191",
            command=lambda: self.set_filter(f"category:{cat_en}")
        )
        btn.pack(fill="x", pady=1)
    
    def create_stat_row(self, label: str, value: str):
        row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=4)
        
        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=("Arial", 11),
            anchor="w",
            text_color="#2d3748"
        )
        label_widget.pack(side="left")
        
        value_widget = ctk.CTkLabel(
            row,
            text=value,
            font=("Arial", 11, "bold"),
            anchor="e",
            text_color="#016191"
        )
        value_widget.pack(side="right")
        
        self.stats_labels[label] = value_widget
    
    def toggle_sort(self, sort_by: str):
        if self.sort_by == sort_by:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_by = sort_by
            self.sort_ascending = True  # Mặc định tăng dần
        
        self.update_sort_buttons()
        
        if self.on_sort_callback:
            self.on_sort_callback(self.sort_by, self.sort_ascending)

    def clear_sort(self):
        self.sort_by = "created_date"
        self.sort_ascending = False
        self.update_sort_buttons()
        
        if self.on_sort_callback:
            self.on_sort_callback(self.sort_by, self.sort_ascending)

    def update_sort_buttons(self):
        # Reset tất cả nút
        sort_buttons = {
            "created_date": self.btn_date,
            "priority": self.btn_priority, 
            "title": self.btn_title
        }
        
        for btn in sort_buttons.values():
            btn.configure(
                fg_color="transparent",
                text_color="#016191",
                border_width=1,
                border_color="#adcace"
            )
        
        # Cập nhật text dựa trên loại sắp xếp và chiều
        if self.sort_by == "created_date":
            text = "Cũ nhất" if self.sort_ascending else "Mới nhất"
            self.btn_date.configure(text=text)
        elif self.sort_by == "priority":
            text = "Thấp→Cao" if self.sort_ascending else "Cao→Thấp"
            self.btn_priority.configure(text=text)
        elif self.sort_by == "title":
            text = "A→Z" if self.sort_ascending else "Z→A"
            self.btn_title.configure(text=text)
        
        # Highlight nút đang active
        if self.sort_by in sort_buttons:
            sort_buttons[self.sort_by].configure(
                fg_color="#0197ca",
                text_color="white",
                border_width=0
            )
        
        # Cập nhật nút "Bỏ sắp xếp"
        if self.sort_by is None:
            self.btn_clear_sort.configure(
                fg_color="transparent",
                text_color="#78a7bc"
            )
        else:
            self.btn_clear_sort.configure(
                fg_color="#f0f9fc",
                text_color="#016191"
            )
    def set_filter(self, filter_type: str):
        self.current_filter = filter_type
        
        # Reset tất cả nút
        for btn in [self.btn_all, self.btn_starred, self.btn_archived,
                   self.btn_urgent, self.btn_high, self.btn_medium, self.btn_low]:
            btn.configure(fg_color="transparent", text_color="#016191")
        
        # Highlight active button
        if filter_type == "all":
            self.btn_all.configure(fg_color="#0197ca", text_color="#FFFFFF")
        elif filter_type == "starred":
            self.btn_starred.configure(fg_color="#0197ca", text_color="#FFFFFF")
        elif filter_type == "archived":
            self.btn_archived.configure(fg_color="#0197ca", text_color="#FFFFFF")
        elif filter_type == "priority:urgent":
            self.btn_urgent.configure(fg_color="#0197ca", text_color="#DC2626")
        elif filter_type == "priority:high":
            self.btn_high.configure(fg_color="#0197ca", text_color="#EA580C")
        elif filter_type == "priority:medium":
            self.btn_medium.configure(fg_color="#0197ca", text_color="#CA8A04")
        elif filter_type == "priority:low":
            self.btn_low.configure(fg_color="#0197ca", text_color="#16A34A")
        
        if self.on_filter_callback:
            self.on_filter_callback(filter_type)
    
    def update_stats(self, stats: dict):
        if "total_notes" in stats:
            self.stats_labels["Tổng số"].configure(text=str(stats["total_notes"]))
        
        if "starred" in stats:
            self.stats_labels["Quan trọng"].configure(text=str(stats["starred"]))
        
        if "due_this_week" in stats:
            self.stats_labels["Tuần này"].configure(text=str(stats["due_this_week"]))
    
    def update_categories(self, categories: list):
        # Xóa các nút danh mục cũ
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        # Thêm danh mục mới
        for category in categories[:5]:  # Giới hạn 5 danh mục
            self.create_category_button(category)
        
        # Thêm nút "Xem thêm" nếu có nhiều danh mục
        if len(categories) > 5:
            more_btn = ctk.CTkButton(
                self.categories_frame,
                text=f"+ {len(categories) - 5} danh mục khác...",
                font=("Arial", 10),
                fg_color="transparent",
                text_color="#78a7bc",
                hover_color="#d4dada",
                anchor="w",
                height=28,
                command=self.show_all_categories
            )
            more_btn.pack(fill="x", pady=2)
    
    def show_all_categories(self):
        logger.info("Hiển thị tất cả danh mục")