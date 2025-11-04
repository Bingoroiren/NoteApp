import customtkinter as ctk
from app.models.note_model import NoteModel

class NoteDetail(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10)
        
        self.note_model = NoteModel()
        self.current_note_id = None
        self.parent = parent  # Thêm để refresh list
        
       
        
        # Nút tạo mới
        ctk.CTkButton(
            header,
            text="+ Tạo mới",
            command=self.create_new_note,
            width=100,
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="right", padx=5)
        
        # Title input
        self.title_entry = ctk.CTkEntry(
            self,
            placeholder_text="Tiêu đề ghi chú",
            height=40,
            font=("Segoe UI", 14)
        )
        self.title_entry.pack(fill="x", padx=20, pady=(0, 10))
        
         # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Chi tiết ghi chú",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left")
        
        # Content input
        self.content_text = ctk.CTkTextbox(
            self,
            font=("Segoe UI", 12),
            wrap="word"
        )
        self.content_text.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Lưu",
            command=self.save_note,
            width=100
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Xóa",
            command=self.delete_note,
            fg_color="red",
            hover_color="darkred",
            width=100
        )
        self.delete_btn.pack(side="left", padx=5)
        
        # Label trạng thái
        self.status_label = ctk.CTkLabel(
            btn_frame,
            text="",
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=10)
    
    def create_new_note(self):
        """Tạo note mới"""
        title = self.title_entry.get().strip() or "Ghi chú mới"
        content = self.content_text.get("1.0", "end-1c").strip()
        
        # Tạo note trong database
        note_id = self.note_model.create(
            title=title,
            content=content,
            category=self.parent.current_category
        )
        
        self.current_note_id = note_id
        self.status_label.configure(text="Đã tạo mới", text_color="green")
        
        # Refresh danh sách
        self.parent.load_notes()
        
        # Reset sau 2 giây
        self.after(2000, lambda: self.status_label.configure(text=""))
    
    def load_note(self, note_id):
        """Load note từ database"""
        self.current_note_id = note_id
        note = self.note_model.read_by_id(note_id)
        
        if note:
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, note.get("title", ""))
            
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", note.get("content", ""))
            
            self.status_label.configure(text="Đã tải", text_color="gray")
    
    def save_note(self):
        """Lưu note (tạo mới hoặc cập nhật)"""
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()
        
        if not title and not content:
            self.status_label.configure(text=" Vui lòng nhập nội dung", text_color="orange")
            return
        
        if self.current_note_id:
            # Cập nhật note đã có
            success = self.note_model.update(
                self.current_note_id,
                title=title or "Không có tiêu đề",
                content=content
            )
            
            if success:
                self.status_label.configure(text=" Đã lưu", text_color="green")
                self.parent.load_notes()  # Refresh list
            else:
                self.status_label.configure(text=" Lỗi lưu", text_color="red")
        else:
            # Tạo note mới nếu chưa có
            self.create_new_note()
        
        # Reset sau 2 giây
        self.after(2000, lambda: self.status_label.configure(text=""))
    
    def delete_note(self):
        """Xóa note"""
        if not self.current_note_id:
            self.status_label.configure(text="Chưa có ghi chú để xóa", text_color="orange")
            return
        
        # Hỏi xác nhận (optional)
        success = self.note_model.delete(self.current_note_id)
        
        if success:
            self.status_label.configure(text=" Đã xóa", text_color="green")
            self.clear_form()
            self.parent.load_notes()  # Refresh list
        else:
            self.status_label.configure(text=" Lỗi xóa", text_color="red")
        
        # Reset sau 2 giây
        self.after(2000, lambda: self.status_label.configure(text=""))
    
    def clear_form(self):
        """Xóa form"""
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        self.current_note_id = None
        self.status_label.configure(text="")