import customtkinter as ctk
import os
import sys
from dotenv import load_dotenv
import logging

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('noteapp.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from app.models.database import db_instance
from app.controllers.note_controller import NoteController
from app.gui.components.sidebar import Sidebar
from app.gui.components.note_list import NoteList
from app.gui.components.note_detail import NoteDetail
from app.gui.components.add_note import AddNoteDialog


class NoteApp(ctk.CTk):
    """Ứng dụng ghi chú tối ưu"""
    
    COLORS = {
        'primary': '#016191',
        'secondary': '#0197ca',
        'accent': '#78a7bc',
        'bg_main': '#F5F7FA',
        'bg_surface': '#FFFFFF',
        'bg_hover': '#e8f4f8',
        'bg_sidebar': '#e8f4f8',
        'text_primary': '#2d3748',
        'text_secondary': '#78a7bc',
        'text_heading': '#016191',
        'border': '#adcace',
        'success': '#16A34A',
        'warning': '#CA8A04',
        'danger': '#DC2626',
    }
    
    def __init__(self):
        super().__init__()
        
        # Cấu hình cửa sổ - THU GỌN HƠN
        self.title("NoteApp")
        self.geometry("1200x700")  # Nhỏ gọn hơn từ 1400x800
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=self.COLORS['bg_main'])
        
        self.controller = NoteController()
        
        if not db_instance.test_connection():
            self.show_error("Kết nối database thất bại")
            return
        
        self.current_filter = "all"
        self.current_note_id = None
        self.selected_notes = []
        self.sort_by = "created_date"  # Mặc định sắp xếp
        self.sort_ascending = False
        
        self.setup_ui()
        self.refresh_notes()
        
        logger.info("Ứng dụng khởi động thành công")
    
    def setup_ui(self):
        """Thiết lập giao diện với layout tối ưu"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar - GIỮ NGUYÊN KÍCH THƯỚC
        self.sidebar = Sidebar(self, self.on_filter_change, self.on_sort_change)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Panel bên phải
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)  # Note list
        self.right_panel.grid_columnconfigure(1, weight=0, minsize=0)    # Note detail - ẨN BAN ĐẦU
        self.right_panel.grid_rowconfigure(1, weight=1)
        
        # Thanh công cụ trên - GỌN HƠN
        top_bar = ctk.CTkFrame(
            self.right_panel, 
            height=50,  # Giảm từ 60
            fg_color=self.COLORS['bg_surface'],
            corner_radius=8
        )
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        top_bar.grid_columnconfigure(0, weight=1)
        
        # Ô tìm kiếm - NHỎ GỌN HƠN
        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="Tìm kiếm...",
            height=35,  # Giảm từ 40
            font=("Arial", 13),
            fg_color=self.COLORS['bg_main'],
            border_color=self.COLORS['accent'],
            text_color=self.COLORS['text_primary']
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Nút thêm ghi chú - DÙNG CHỮ
        add_btn = ctk.CTkButton(
            top_bar,
            text="Thêm ghi chú",
            width=120,
            height=35,
            font=("Arial", 13, "bold"),
            fg_color=self.COLORS['secondary'],
            hover_color=self.COLORS['primary'],
            text_color="white",
            corner_radius=6,
            command=self.add_note
        )
        add_btn.grid(row=0, column=1, padx=10, pady=8)
        
        # Danh sách ghi chú
        self.note_list = NoteList(
            self.right_panel,
            self.on_note_select,
            self.on_star_click,
            self.on_note_delete
        )
        self.note_list.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # Chi tiết ghi chú - ẨN BAN ĐẦU
        self.note_detail = NoteDetail(
            self.right_panel,
            self.on_note_update,
            self.on_attachment_add,
            self.on_attachment_delete,
            self.on_note_close  # Thêm callback đóng
        )
        # KHÔNG GRID BAN ĐẦU - chỉ grid khi chọn note
        self.note_detail_visible = False
    
    def on_note_select(self, note_id: str):
        """Xử lý chọn ghi chú - HIỆN NOTE DETAIL"""
        self.current_note_id = note_id
        
        try:
            note = self.controller.get_note(note_id)
            if note:
                # Hiện note detail với hiệu ứng
                if not self.note_detail_visible:
                    self.right_panel.grid_columnconfigure(0, weight=2)  # Note list chiếm 2 phần
                    self.right_panel.grid_columnconfigure(1, weight=3)  # Note detail chiếm 3 phần
                    self.note_detail.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
                    self.note_detail_visible = True
                
                self.note_detail.display_note(note)
                self.note_list.select_note(note_id)
        except Exception as e:
            logger.error(f"Lỗi tải ghi chú: {str(e)}")
            self.show_error("Không thể tải ghi chú")
    
    def on_note_close(self):
        """Đóng note detail và reset layout về trạng thái ban đầu"""
        if self.note_detail_visible:
            # Reset grid weights về trạng thái ban đầu
            self.right_panel.grid_columnconfigure(0, weight=1)  # Note list chiếm toàn bộ
            self.right_panel.grid_columnconfigure(1, weight=0)  # Note detail không chiếm chỗ
            
            # Ẩn note detail
            self.note_detail.grid_forget()
            self.note_detail_visible = False
            
            # Reset các biến trạng thái
            self.current_note_id = None
            self.note_list.clear_selection()
            
            # Cập nhật layout ngay lập tức
            self.right_panel.update_idletasks()
            logger.info("Đã đóng note detail và reset layout")
    def refresh_notes(self):
        """Làm mới danh sách ghi chú với sắp xếp"""
        try:
            # Lấy notes theo filter
            if self.current_filter == "all":
                notes = self.controller.get_all_notes(
                    include_archived=False,
                    sort_by=self.sort_by,
                    ascending=self.sort_ascending
                )
            elif self.current_filter == "starred":
                notes = self.controller.note_model.get_starred_notes()
            elif self.current_filter == "archived":
                notes = self.controller.note_model.get_archived_notes()
            elif self.current_filter.startswith("category:"):
                category = self.current_filter.split(":")[1]
                notes = self.controller.note_model.get_notes_by_category(category)
            elif self.current_filter.startswith("priority:"):
                priority = self.current_filter.split(":")[1]
                notes = self.controller.note_model.get_notes_by_priority(priority)
            else:
                notes = self.controller.get_all_notes(
                    sort_by=self.sort_by,
                    ascending=self.sort_ascending
                )
            
            # Áp dụng sắp xếp thủ công nếu cần
            notes = self.apply_sorting(notes)
            
            self.note_list.update_notes(notes)
            
            # Cập nhật thống kê sidebar
            stats = self.controller.get_statistics()
            self.sidebar.update_stats(stats)
            
        except Exception as e:
            logger.error(f"Lỗi làm mới ghi chú: {str(e)}")
            self.show_error("Không thể làm mới danh sách")
    
    def apply_sorting(self, notes: list) -> list:
        """Áp dụng sắp xếp cho notes"""
        if self.sort_by == "priority":
            priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
            notes.sort(
                key=lambda n: priority_order.get(n.get('priority', 'medium'), 2),
                reverse=not self.sort_ascending
            )
        elif self.sort_by == "title":
            notes.sort(
                key=lambda n: n.get('title', '').lower(),
                reverse=not self.sort_ascending
            )
        elif self.sort_by == "created_date":
            notes.sort(
                key=lambda n: n.get('created_date', ''),
                reverse=not self.sort_ascending
            )
        
        return notes
    
    def on_filter_change(self, filter_type: str):
        """Xử lý thay đổi bộ lọc"""
        self.current_filter = filter_type
        self.refresh_notes()
    
    def on_sort_change(self, sort_by: str, ascending: bool):
        """Xử lý thay đổi sắp xếp - TÍNH NĂNG MỚI"""
        self.sort_by = sort_by
        self.sort_ascending = ascending
        self.refresh_notes()
        logger.info(f"Sắp xếp theo: {sort_by}, tăng dần: {ascending}")
    
    def on_search(self, event=None):
        """Xử lý tìm kiếm"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.refresh_notes()
            return
        
        try:
            notes = self.controller.search_notes(search_term)
            notes = self.apply_sorting(notes)
            self.note_list.update_notes(notes)
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm: {str(e)}")
    
    def add_note(self):
        """Mở dialog thêm ghi chú"""
        dialog = AddNoteDialog(self, self.controller)
        self.wait_window(dialog)
        self.refresh_notes()
    
    def on_note_update(self, note_id: str, **kwargs):
        """Xử lý cập nhật ghi chú"""
        try:
            if self.controller.update_note(note_id, **kwargs):
                self.refresh_notes()
                note = self.controller.get_note(note_id)
                if note and self.note_detail_visible:
                    self.note_detail.display_note(note)
        except Exception as e:
            logger.error(f"Lỗi cập nhật: {str(e)}")
            self.show_error("Không thể cập nhật ghi chú")
    
    def on_star_click(self, note_id: str):
        """Xử lý đánh dấu sao"""
        try:
            if self.controller.toggle_star(note_id):
                self.refresh_notes()
                if self.current_note_id == note_id and self.note_detail_visible:
                    note = self.controller.get_note(note_id)
                    if note:
                        self.note_detail.display_note(note)
        except Exception as e:
            logger.error(f"Lỗi đánh dấu sao: {str(e)}")
    
    def on_note_delete(self, note_id: str):
        """Xử lý xóa ghi chú - ĐÃ SỬA"""
        try:
            result = self.show_confirm(
                "Xác nhận xóa",
                "Bạn có chắc chắn muốn xóa ghi chú này không?"
            )
            
            if result:
                if self.controller.delete_note(note_id):
                    self.refresh_notes()
                    if self.current_note_id == note_id:
                        self.on_note_close()
                else:
                    self.show_error("Không thể xóa ghi chú")
        except Exception as e:
            logger.error(f"Lỗi xóa: {str(e)}")
            self.show_error("Không thể xóa ghi chú")
    
    def on_attachment_add(self, note_id: str, file_path: str):
        """Xử lý thêm tệp đính kèm"""
        try:
            attachment_id = self.controller.add_attachment(note_id, file_path)
            if attachment_id:
                note = self.controller.get_note(note_id)
                if note and self.note_detail_visible:
                    self.note_detail.display_note(note)
            else:
                self.show_error("Không thể thêm tệp")
        except Exception as e:
            logger.error(f"Lỗi thêm tệp: {str(e)}")
            self.show_error("Không thể thêm tệp đính kèm")
    
    def on_attachment_delete(self, note_id: str, attachment_id: str):
        """Xử lý xóa tệp đính kèm"""
        try:
            result = self.show_confirm(
                "Xác nhận xóa",
                "Bạn có chắc chắn muốn xóa tệp này không?"
            )
            
            if result:
                if self.controller.delete_attachment(attachment_id):
                    note = self.controller.get_note(note_id)
                    if note and self.note_detail_visible:
                        self.note_detail.display_note(note)
                else:
                    self.show_error("Không thể xóa tệp")
        except Exception as e:
            logger.error(f"Lỗi xóa tệp: {str(e)}")
            self.show_error("Không thể xóa tệp")
    
    def show_error(self, message: str):
        """Hiển thị thông báo lỗi - GỌN HƠN"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Lỗi")
        dialog.geometry("350x180")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=self.COLORS['bg_main'])
        
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"350x180+{x}+{y}")
        
        ctk.CTkLabel(
            dialog,
            text="⚠️",
            font=("Arial", 35)
        ).pack(pady=(25, 10))
        
        ctk.CTkLabel(
            dialog,
            text=message,
            font=("Arial", 12),
            text_color=self.COLORS['text_primary'],
            wraplength=300
        ).pack(pady=8)
        
        ctk.CTkButton(
            dialog,
            text="Đóng",
            width=90,
            fg_color=self.COLORS['secondary'],
            hover_color=self.COLORS['primary'],
            text_color="white",
            command=dialog.destroy
        ).pack(pady=10)
    
    def show_confirm(self, title: str, message: str) -> bool:
        """Hiển thị dialog xác nhận - GỌN HƠN"""
        result = {"confirmed": False}
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x180")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=self.COLORS['bg_main'])
        
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"350x180+{x}+{y}")
        
        ctk.CTkLabel(
            dialog,
            text="⚠️",
            font=("Arial", 35)
        ).pack(pady=(18, 8))
        
        ctk.CTkLabel(
            dialog,
            text=message,
            font=("Arial", 12),
            text_color=self.COLORS['text_primary'],
            wraplength=300
        ).pack(pady=8)
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=15)
        
        def on_confirm():
            result["confirmed"] = True
            dialog.destroy()
        
        def on_cancel():
            result["confirmed"] = False
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame,
            text="Hủy",
            width=100,
            fg_color=self.COLORS['border'],
            hover_color=self.COLORS['accent'],
            text_color=self.COLORS['text_primary'],
            command=on_cancel
        ).pack(side="left", padx=8)
        
        ctk.CTkButton(
            button_frame,
            text="Xác nhận",
            width=100,
            fg_color=self.COLORS['danger'],
            hover_color="#B91C1C",
            text_color="white",
            command=on_confirm
        ).pack(side="left", padx=8)
        
        self.wait_window(dialog)
        return result["confirmed"]
    
    def on_closing(self):
        """Xử lý đóng cửa sổ"""
        logger.info("Đóng ứng dụng")
        db_instance.close_connection()
        self.destroy()


def main():

    try:
        app = NoteApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng: {str(e)}")
        print(f"Lỗi khởi động ứng dụng: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()