import customtkinter as ctk
from datetime import datetime
import tkinter.messagebox

from app.gui.components.sidebar import Sidebar
# Tách riêng import
from app.gui.components.options_menu import OptionsMenu, SortByMenu
from app.models.note_model import NoteModel


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ===== WINDOW =====
        self.title("NOTES APP")
        self.geometry("1100x700")
        self.configure(fg_color=("#1E1E1E", "#1E1E1E"))

        # ... (phần model, grid, state) ...
        self.note_model = NoteModel()

        self.grid_columnconfigure(0, weight=0)   # sidebar
        self.grid_columnconfigure(1, weight=1)   # main
        self.grid_rowconfigure(0, weight=1)

        self.current_category = "Ngày của Tôi"
        self.options_menu_visible = False

        # ... (phần sidebar) ...
        self.sidebar = Sidebar(self, self.on_category_change, auto_select=False)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # ===== MAIN (GIỮA) =====
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # ... (phần header, list, add_bar) ...
        # Header
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1) 
        header.grid_columnconfigure(1, weight=0) 
        title_date_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_date_frame.grid(row=0, column=0, sticky="w")
        self.header_label = ctk.CTkLabel(
            title_date_frame, text="My Day",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#FFFFFF"
        )
        self.header_label.pack(anchor="w", padx=10, pady=(10, 5))
        self.date_label = ctk.CTkLabel(
            title_date_frame, text=self.get_current_date(),
            font=ctk.CTkFont(size=16), text_color="#BBBBBB"
        )
        self.date_label.pack(anchor="w", padx=10, pady=(0, 10))
        self.options_btn = ctk.CTkButton(
            header, text="...", font=ctk.CTkFont(size=20, weight="bold"),
            width=40, height=40, fg_color="transparent",
            hover_color=("#E0E0E0", "#333333"),
            command=self.toggle_options_menu
        )
        self.options_btn.grid(row=0, column=1, sticky="e", padx=10, pady=10)
        # List
        self.list_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#494545")
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 20))
        self.note_widgets = []
        # Add bar
        add_bar = ctk.CTkFrame(self.main_frame, fg_color="#F9FAFB", corner_radius=25)
        add_bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.add_entry = ctk.CTkEntry(
            add_bar, placeholder_text="Add a task",
            height=40, corner_radius=25, font=ctk.CTkFont(size=14)
        )
        self.add_entry.pack(side="left", padx=(15, 10), pady=10, fill="x", expand=True)
        self.add_entry.bind("<Return>", self.on_add_task)
        self.add_btn = ctk.CTkButton(
            add_bar, text="Thêm", width=90, height=38, corner_radius=20,
            fg_color="#3B82F6", hover_color="#2563EB", text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"), command=self.on_add_task
        )
        self.add_btn.pack(side="right", padx=(0, 15), pady=10)


        # ===== KHỞI TẠO CẢ HAI MENU =====
        
        # 1. Khởi tạo menu con (SortByMenu)
        #    Nó là con của self.main_frame
        self.sort_by_menu = SortByMenu(
            self.main_frame, 
            placeholder_callback=self.placeholder_callback 
        )

        # 2. Khởi tạo menu cha (OptionsMenu)
        #    Nó cũng là con của self.main_frame
        #    Truyền menu con vào cho nó
        self.options_menu = OptionsMenu(
            self.main_frame, 
            on_delete_category=self.on_delete_category_request,
            sort_menu_instance=self.sort_by_menu,
            placeholder_callback=self.placeholder_callback
        )

        # ... (phần initial data) ...
        self.sidebar.select_category("Ngày của Tôi")
        self.on_category_change("Ngày của Tôi") 

    # ===== Thêm hàm callback này =====
    def placeholder_callback(self):
        """Hàm tạm thời cho các nút chưa có chức năng."""
        tkinter.messagebox.showinfo(
            "Chưa cài đặt",
            "Chức năng này chưa được cài đặt."
        )

    # ... (các hàm helpers, load_notes, on_add_task, v.v. giữ nguyên) ...
    def get_current_date(self) -> str:
        return datetime.now().strftime("%A, %B %d")

    def clear_widgets(self):
        for w in self.note_widgets:
            w.destroy()
        self.note_widgets.clear()

    def load_notes(self):
        self.clear_widgets()
        category = "My Day" if self.current_category == "Ngày của Tôi" else self.current_category
        notes = self.note_model.read_all(category=category)
        if not notes:
            lbl = ctk.CTkLabel(
                self.list_frame,
                text="Chưa có ghi chú nào\nThêm ghi chú mới để bắt đầu!",
                font=ctk.CTkFont(size=14), text_color="#888888", justify="center"
            )
            lbl.pack(pady=20)
            self.note_widgets.append(lbl)
            return
        for note in notes:
            self._add_note_widget(note)

    def _add_note_widget(self, note):
        row = ctk.CTkFrame(self.list_frame, fg_color="#F9FAFB", corner_radius=10)
        row.pack(fill="x", padx=10, pady=5)
        var = ctk.BooleanVar(value=note.get("completed", False))
        cb = ctk.CTkCheckBox(
            row, text=note.get("title", "Untitled"), variable=var,
            font=ctk.CTkFont(size=15), onvalue=True, offvalue=False,
            command=lambda n=note: self.toggle_completed(n)
        )
        cb.pack(anchor="w", padx=15, pady=10, fill="x", expand=True)
        if note.get("completed", False):
            cb.configure(font=ctk.CTkFont(size=15, overstrike=True))
        self.note_widgets.append(row)

    def on_add_task(self, event=None):
        title = self.add_entry.get().strip()
        if not title: return
        category_to_add = "My Day" if self.current_category == "Ngày của Tôi" else self.current_category
        self.note_model.create(title=title, category=category_to_add)
        self.add_entry.delete(0, "end")
        self.load_notes()

    def toggle_completed(self, note):
        self.note_model.toggle_completed(note["_id"])
        self.load_notes()

    def on_category_change(self, category: str):
        self.current_category = category
        self.header_label.configure(text=category)
        self.load_notes()
        self.options_menu.update_category_info(category)
        if self.options_menu_visible:
            self.toggle_options_menu()

    
    # ===== LOGIC CHO MENU TÙY CHỌN =====
    
    def toggle_options_menu(self):
        """Hiển thị hoặc ẩn menu tùy chọn."""
        if self.options_menu_visible:
            # --- Ẩn menu ---
            # Gọi hàm hide_sort_menu() của options_menu
            # nó sẽ tự động ẩn self.sort_by_menu
            self.options_menu.hide_sort_menu()
            
            self.options_menu.place_forget()
            self.options_menu_visible = False
        else:
            # --- Hiện menu ---
            self.options_btn.update_idletasks() 
            btn_x = self.options_btn.winfo_x()
            btn_y = self.options_btn.winfo_y()
            btn_width = self.options_btn.winfo_width()
            btn_height = self.options_btn.winfo_height()
            
            menu_x = btn_x + btn_width
            menu_y = btn_y + btn_height + 5

            self.options_menu.place(x=menu_x, y=menu_y, anchor="ne")
            self.options_menu_visible = True
    
    
    def on_delete_category_request(self):
        """Được gọi khi nhấn nút 'Delete list' trong OptionsMenu."""
        self.toggle_options_menu()
        
        confirmed = tkinter.messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa danh sách '{self.current_category}' không?\n"
            "Tất cả các ghi chú trong danh sách này cũng sẽ bị xóa."
        )
        
        if confirmed:
            print(f"Placeholder: Người dùng ĐÃ XÁC NHẬN xóa category: {self.current_category}")
            tkinter.messagebox.showinfo(
                "Đã xóa (Giả lập)",
                f"Đã xóa danh sách '{self.current_category}'."
            )
        else:
            print(f"Placeholder: Người dùng đã HỦY xóa category: {self.current_category}")
