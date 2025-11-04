import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_category_change, auto_select=True):  # ← Thêm tham số này
        super().__init__(parent, width=250, corner_radius=0)
        
        self.on_category_change = on_category_change
        self.auto_select = auto_select  # ← Lưu giá trị
        
        # User info
        user_frame = ctk.CTkFrame(self, fg_color="transparent")
        user_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            user_frame, 
            text="yirpng@gmail.com",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")
        
        # Search
        self.search_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Tìm kiếm",
            height=35
        )
        self.search_entry.pack(fill="x", padx=10, pady=(0, 20))
        
        # Categories
        categories = [
            ("☀️", "Ngày của Tôi"),
            ("⭐", "Quan trọng"),
            ("📋", "Đã lập kế hoạch"),
            ("👤", "Đã giao cho tôi"),
            ("📁", "Tác vụ"),
            ("💡", "Bật đầu"),
        ]
        
        self.category_buttons = {}
        for icon, name in categories:
            btn = ctk.CTkButton(
                self,
                text=f"{icon}  {name}",
                anchor="w",
                fg_color="transparent",
                hover_color=("#3b3b3b", "#2b2b2b"),
                height=40,
                command=lambda n=name: self.select_category(n)
            )
            btn.pack(fill="x", padx=5, pady=2)
            self.category_buttons[name] = btn
        
        # Auto-select default category nếu auto_select=True
        if self.auto_select:
            self.select_category("Ngày của Tôi")
    
    def select_category(self, category):
        # Reset all buttons
        for btn in self.category_buttons.values():
            btn.configure(fg_color="transparent")
        
        # Highlight selected
        if category in self.category_buttons:
            self.category_buttons[category].configure(fg_color=("#2b2b2b", "#1f1f1f"))
        
        # Callback
        self.on_category_change(category)