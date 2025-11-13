import customtkinter as ctk
import tkinter.messagebox

# ===================================================================
# LỚP MENU CON MỚI: SortByMenu (Giữ nguyên)
# ===================================================================
class SortByMenu(ctk.CTkFrame):
    def __init__(self, master, placeholder_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color=("#F2F2F2", "#2B2B2B"),
                         corner_radius=10,
                         border_width=2,
                         border_color=("#E0E0E0", "#333333"))
        self.grid_columnconfigure(0, weight=1)
        buttons = [
            "Importance", "Due date", "Added to My Day",
            "Alphabetically", "Creation date"
        ]
        for i, text in enumerate(buttons):
            btn = ctk.CTkButton(
                self, text=text, fg_color="transparent",
                anchor="w", command=placeholder_callback
            )
            btn.grid(row=i, column=0, sticky="ew", padx=10, pady=5)


# ===================================================================
# LỚP MENU CHÍNH: OptionsMenu (Đã cập nhật)
# ===================================================================
class OptionsMenu(ctk.CTkFrame):
    def __init__(self, master, on_delete_category, sort_menu_instance, placeholder_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.on_delete_category_callback = on_delete_category
        self.sort_by_menu = sort_menu_instance
        self.placeholder_callback = placeholder_callback
        
        # --- ĐÃ XÓA TIMER (self._sort_menu_hide_job) ---

        self.configure(width=320, height=700,
                         fg_color=("#F2F2F2", "#2B2B2B"), 
                         corner_radius=15,
                         border_width=2,
                         border_color=("#E0E0E0", "#333333"))
                         
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        
        current_row = 0

        # === CÁC WIDGET CON VÀ GÁN SỰ KIỆN ===

        # 1. Tiêu đề
        self.title_label = ctk.CTkLabel(
            self, text="Untitled list", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=current_row, column=0, sticky="ew", padx=20, pady=20)
        current_row += 1
        # Gán sự kiện ẩn
        self.title_label.bind("<Enter>", self.hide_sort_menu)

        # 2. Nhóm 1: Tùy chọn
        self.rename_btn = ctk.CTkButton(
            self, text="Rename list", fg_color="transparent", anchor="w",
            command=self.placeholder_callback 
        )
        self.rename_btn.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1
        self.rename_btn.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn
        
        self.move_list_btn = ctk.CTkButton(
            self, text="Move list to...", fg_color="transparent", anchor="w",
            command=self.placeholder_callback 
        )
        self.move_list_btn.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1
        self.move_list_btn.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn

        self.remove_group_btn = ctk.CTkButton(
            self, text="Remove from group", fg_color="transparent", anchor="w",
            command=self.placeholder_callback 
        )
        self.remove_group_btn.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1
        self.remove_group_btn.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn
        
        # NÚT SORT BY (NÚT ĐẶC BIỆT)
        self.sort_btn = ctk.CTkButton(
            self, text="< Sort by", fg_color="transparent", 
            anchor="w", command=None
        )
        self.sort_btn.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1
        # Gán sự kiện HIỆN
        self.sort_btn.bind("<Enter>", self.on_enter_sort_btn)
        # Không cần bind <Leave> nữa

        # 3. Nhóm 2: Theme
        self.theme_label = ctk.CTkLabel(
            self, text="Theme", anchor="w",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.theme_label.grid(row=current_row, column=0, sticky="ew", padx=20, pady=(15, 5))
        current_row += 1
        self.theme_label.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn

        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.grid(row=current_row, column=0, sticky="ew", padx=15)
        current_row += 1
        theme_frame.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn
        
        for i in range(5):
            theme_frame.grid_columnconfigure(i, weight=1, uniform="theme_col")
        all_swatches = [
            ["#3B82F6", "#6D28D9", "#EC4899", "#E11D48", "#10B981"],
            ["#14B8A6", "#06B6D4", "#6366F1", "#A855F7", "#F472B6"],
            ["#F97316", "#EAB308", "#84CC16", "#22C55E", "#0891B2"],
            ["#0EA5E9", "#8B5CF6", "#D946EF", "#EF4444", "#F59E0B"],
        ]
        for r, row_items in enumerate(all_swatches):
            for c, color in enumerate(row_items):
                btn = ctk.CTkButton(
                    theme_frame, text="", height=40,
                    fg_color=color, corner_radius=10,
                    command=self.placeholder_callback 
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="ew")
                btn.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn

        # 4. Phân cách 1
        separator1 = ctk.CTkFrame(self, height=1, fg_color=("#E0E0E0", "#333333"))
        separator1.grid(row=current_row, column=0, sticky="ew", padx=20, pady=15)
        current_row += 1
        separator1.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn

        # 5. Nhóm 3: Chia sẻ / In ấn
        self.print_btn = ctk.CTkButton(
            self, text="Print list", fg_color="transparent", anchor="w",
            command=self.placeholder_callback 
        )
        self.print_btn.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1
        self.print_btn.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn

        self.email_btn = ctk.CTkButton(
            self, text="Email list", fg_color="transparent", anchor="w",
            command=self.placeholder_callback 
        )
        self.email_btn.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1
        self.email_btn.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn

        self.pin_btn = ctk.CTkButton(
            self, text="Pin to Start", fg_color="transparent", anchor="w",
            command=self.placeholder_callback 
        )
        self.pin_btn.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1
        self.pin_btn.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn

        # 6. Phân cách 2
        separator2 = ctk.CTkFrame(self, height=1, fg_color=("#E0E0E0", "#333333"))
        separator2.grid(row=current_row, column=0, sticky="ew", padx=20, pady=15)
        current_row += 1
        separator2.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn
        
        # 7. Dòng trống co giãn
        self.grid_rowconfigure(current_row, weight=1)
        current_row += 1

        # 8. Nút Delete
        self.delete_btn = ctk.CTkButton(
            self, text="Delete list", fg_color="transparent", text_color="#F87171",
            hover_color="#DC2626", anchor="w",
            command=self.on_delete_category_callback
        )
        self.delete_btn.grid(row=current_row, column=0, sticky="sew", padx=20, pady=20)
        self.delete_btn.bind("<Enter>", self.hide_sort_menu) # Gán sự kiện ẩn


    # --- CÁC HÀM HOVER (ĐÃ XÓA BỎ TIMER) ---
    
    def on_enter_sort_btn(self, event=None):
        """Gọi khi di chuột vào nút 'Sort by' -> HIỆN MENU CON."""
        self.update_idletasks() 
        self.sort_btn.update_idletasks()
        
        menu_x = self.winfo_x()
        menu_y = self.winfo_y()
        btn_y_relative = self.sort_btn.winfo_y()
        
        # Thêm 1px chồng lấn để đảm bảo không có kẽ hở
        x = menu_x + 1 
        y = menu_y + btn_y_relative
        
        self.sort_by_menu.place(x=x, y=y, anchor="ne") 
        self.sort_by_menu.lift() 

    def hide_sort_menu(self, event=None):
        """Gọi khi di chuột vào BẤT CỨ NÚT NÀO KHÁC -> ẨN MENU CON."""
        self.sort_by_menu.place_forget()
        
    # --- XÓA CÁC HÀM: on_enter_sort_menu, on_leave_sort_area ---
        
    def update_category_info(self, category_name: str):
        self.title_label.configure(text=category_name)
        is_default = category_name in ["Ngày của Tôi", "Important", "Tasks"]
        
        if hasattr(self, 'delete_btn'):
            if is_default:
                self.delete_btn.configure(state="disabled", text_color="#555555")
            else:
                self.delete_btn.configure(state="normal", text_color="#F87171")