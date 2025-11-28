import customtkinter as ctk
from typing import Callable, Dict
from datetime import datetime
import logging
from tkinter import filedialog
from PIL import Image, ImageTk
import os

logger = logging.getLogger(__name__)


class NoteDetail(ctk.CTkFrame):
    
    COLORS = {
        'primary': '#016191',
        'secondary': '#0197ca',
        'accent': '#78a7bc',
        'bg_main': '#F5F7FA',
        'bg_surface': '#FFFFFF',
        'bg_hover': '#e8f4f8',
        'bg_card': '#f0f9fc',
        'text_primary': '#2d3748',
        'text_secondary': '#78a7bc',
        'text_heading': '#016191',
        'border': '#adcace',
        'danger': '#DC2626',
    }
    
    def __init__(self, parent, on_update: Callable, on_attachment_add: Callable, 
                 on_attachment_delete: Callable, on_close: Callable):
        super().__init__(parent, fg_color=self.COLORS['bg_surface'], corner_radius=10)
        
        self.on_update = on_update
        self.on_attachment_add = on_attachment_add
        self.on_attachment_delete = on_attachment_delete
        self.on_close = on_close
        
        self.current_note = None
        self.is_editing = False
        self.preview_window = None
        
        self.reminder_window = None
        self.reminder_date_var = None
        self.reminder_time_var = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=55)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Tiêu đề
        self.title_entry = ctk.CTkEntry(
            self.header_frame,
            font=("Arial", 20, "bold"),
            placeholder_text="Tiêu đề",
            height=36,
            border_width=0,
            fg_color="transparent",
            text_color=self.COLORS['text_heading']
        )
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.title_entry.bind("<FocusOut>", self.save_title)
        
        action_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        action_frame.grid(row=0, column=1, sticky="e")
        
        close_btn = ctk.CTkButton(
            action_frame,
            text="Đóng",
            width=65,
            height=32,
            font=("Arial", 12),
            fg_color="transparent",
            hover_color=self.COLORS['bg_hover'],
            text_color=self.COLORS['text_secondary'],
            border_width=2,
            border_color=self.COLORS['border'],
            command=self.close_detail
        )
        close_btn.pack(side="left", padx=2)
        
        # Nút quan trọng
        self.star_btn = ctk.CTkButton(
            action_frame,
            text="Quan trọng",
            width=90,
            height=32,
            font=("Arial", 12),
            fg_color="transparent",
            hover_color=self.COLORS['bg_hover'],
            text_color=self.COLORS['secondary'],
            border_width=2,
            border_color=self.COLORS['secondary'],
            command=self.toggle_star
        )
        self.star_btn.pack(side="left", padx=2)
        
        # Nút lưu trữ
        archive_btn = ctk.CTkButton(
            action_frame,
            text="Lưu trữ",
            width=80,
            height=32,
            font=("Arial", 12),
            fg_color="transparent",
            hover_color=self.COLORS['bg_hover'],
            text_color=self.COLORS['secondary'],
            border_width=2,
            border_color=self.COLORS['secondary'],
            command=self.archive_note
        )
        archive_btn.pack(side="left", padx=2)
        
        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="Xóa",
            width=65,
            height=32,
            font=("Arial", 12),
            fg_color="transparent",
            hover_color="#fee2e2",
            text_color=self.COLORS['danger'],
            border_width=2,
            border_color=self.COLORS['danger'],
            command=self.delete_note
        )
        self.delete_btn.pack(side="left", padx=2)
        
        self.metadata_frame = ctk.CTkFrame(
            self, 
            fg_color=self.COLORS['bg_card'],
            height=70,
            
        )
        self.metadata_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.metadata_frame.grid_columnconfigure(0, weight=1)
        self.metadata_frame.grid_columnconfigure(1, weight=1)
        
        left_meta = ctk.CTkFrame(self.metadata_frame, fg_color="transparent")
        left_meta.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(
            left_meta,
            text="Danh mục:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 5))
        
        self.category_var = ctk.StringVar(value="Chung")
        self.category_menu = ctk.CTkOptionMenu(
            left_meta,
            variable=self.category_var,
            values=["Chung", "Công việc", "Cá nhân", "Ý tưởng", "Nhiệm vụ", "Học tập"],
            width=110,
            height=26,
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            button_color=self.COLORS['primary'],
            button_hover_color=self.COLORS['accent'],
            text_color="white",
            command=self.update_category
        )
        self.category_menu.pack(side="left", padx=3)
        
        ctk.CTkLabel(
            left_meta,
            text="Ưu tiên:",
            font=("Arial", 12)
        ).pack(side="left", padx=(10, 5))
        
        self.priority_var = ctk.StringVar(value="Trung bình")
        self.priority_menu = ctk.CTkOptionMenu(
            left_meta,
            variable=self.priority_var,
            values=["Thấp", "Trung bình", "Cao", "Khẩn cấp"],
            width=110,
            height=26,
            font=("Arial", 12),
            fg_color=self.COLORS['secondary'],
            button_color=self.COLORS['primary'],
            button_hover_color=self.COLORS['accent'],
            text_color="white",
            command=self.update_priority
        )
        self.priority_menu.pack(side="left", padx=3)
        
        # Hàng 2: Ngày tạo
        self.date_label = ctk.CTkLabel(
            self.metadata_frame,
            text="",
            font=("Arial", 10),
            text_color=self.COLORS['text_secondary']
        )
        self.date_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
        
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            border_color="#78a7bc",
            
        )
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 10))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Textbox nội dung
        self.content_text = ctk.CTkTextbox(
            self.content_frame,
            font=("Arial", 12),
            wrap="word",
            border_width=1,
            border_color="#78a7bc",
            fg_color="white",
            text_color=self.COLORS['text_primary']
        )
        self.content_text.grid(row=0, column=0, sticky="nsew", pady=8)
        self.content_text.bind("<KeyRelease>", self.auto_save_content)
        
        tags_frame = ctk.CTkFrame(
            self.content_frame, 
            fg_color=self.COLORS['bg_card'],
            corner_radius=6
            
        )
        tags_frame.grid(row=1, column=0, sticky="ew", pady=8)
        
        ctk.CTkLabel(
            tags_frame,
            text="Nhãn:",
            font=("Arial", 11, "bold"),
            text_color=self.COLORS['text_heading']
        ).pack(side="left", padx=12, pady=8)
        
        self.tags_entry = ctk.CTkEntry(
            tags_frame,
            placeholder_text="Thêm nhãn (phân cách bằng dấu phẩy)",
            height=30,
            border_width=0,
            fg_color="white",
            text_color=self.COLORS['text_primary']
        )
        self.tags_entry.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        self.tags_entry.bind("<Return>", self.update_tags)
        self.reminder_frame = ctk.CTkFrame(
            self.metadata_frame, 
            fg_color="transparent"
        )
        self.reminder_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        self.reminder_frame.grid_columnconfigure(1, weight=1)
        
        # Hàng 1: Ngày đến hạn
        due_date_frame = ctk.CTkFrame(self.reminder_frame, fg_color="transparent")
        due_date_frame.grid(row=0, column=0, sticky="w", pady=2)
        
        ctk.CTkLabel(
            due_date_frame,
            text="Đến hạn:",
            font=("Arial", 11)
        ).pack(side="left", padx=(0, 5))
        
        self.due_date_label = ctk.CTkLabel(
            due_date_frame,
            text="Không có",
            font=("Arial", 11),
            text_color=self.COLORS['text_secondary']
        )
        self.due_date_label.pack(side="left", padx=5)
        
        # Nút quản lý thời hạn
        due_date_btn = ctk.CTkButton(
            due_date_frame,
            text="Đặt hạn",
            width=60,
            height=24,
            font=("Arial", 10),
            fg_color="transparent",
            hover_color=self.COLORS['bg_hover'],
            text_color=self.COLORS['secondary'],
            border_width=1,
            border_color=self.COLORS['secondary'],
            command=self.manage_due_date
        )
        due_date_btn.pack(side="left", padx=5)
        
        # Nút xóa hạn (ban đầu ẩn)
        self.clear_due_date_btn = ctk.CTkButton(
            due_date_frame,
            text="Xóa",
            width=45,
            height=24,
            font=("Arial", 10),
            fg_color="transparent",
            hover_color="#fee2e2",
            text_color=self.COLORS['danger'],
            border_width=1,
            border_color=self.COLORS['danger'],
            command=self.clear_due_date
        )
        self.clear_due_date_btn.pack(side="left", padx=2)
        self.clear_due_date_btn.pack_forget()  # Ẩn ban đầu
        
        # Hàng 2: Nhắc hẹn
        reminder_frame = ctk.CTkFrame(self.reminder_frame, fg_color="transparent")
        reminder_frame.grid(row=1, column=0, sticky="w", pady=2)
        
        ctk.CTkLabel(
            reminder_frame,
            text="Nhắc hẹn:",
            font=("Arial", 11)
        ).pack(side="left", padx=(0, 5))
        
        self.reminder_label = ctk.CTkLabel(
            reminder_frame,
            text="Không có",
            font=("Arial", 11),
            text_color=self.COLORS['text_secondary']
        )
        self.reminder_label.pack(side="left", padx=5)
        
        # Nút quản lý nhắc hẹn
        reminder_btn = ctk.CTkButton(
            reminder_frame,
            text="Đặt nhắc",
            width=65,
            height=24,
            font=("Arial", 10),
            fg_color="transparent",
            hover_color=self.COLORS['bg_hover'],
            text_color=self.COLORS['secondary'],
            border_width=1,
            border_color=self.COLORS['secondary'],
            command=self.manage_reminder
        )
        reminder_btn.pack(side="left", padx=5)
        
        self.clear_reminder_btn = ctk.CTkButton(
            reminder_frame,
            text="Xóa",
            width=45,
            height=24,
            font=("Arial", 10),
            fg_color="transparent",
            hover_color="#fee2e2",
            text_color=self.COLORS['danger'],
            border_width=1,
            border_color=self.COLORS['danger'],
            command=self.clear_reminder
        )
        self.clear_reminder_btn.pack(side="left", padx=2)
        self.clear_reminder_btn.pack_forget()  # Ẩn ban đầu
        
        attachments_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.COLORS['bg_card'],
            corner_radius=6
        )
        attachments_frame.grid(row=2, column=0, sticky="ew", pady=8)
        attachments_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            attachments_frame,
            text="Tệp đính kèm:",
            font=("Arial", 11, "bold"),
            text_color=self.COLORS['text_heading']
        ).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        
        add_attachment_btn = ctk.CTkButton(
            attachments_frame,
            text="Thêm tệp",
            width=85,
            height=26,
            font=("Arial", 11),
            fg_color=self.COLORS['secondary'],
            hover_color=self.COLORS['primary'],
            text_color="white",
            command=self.add_attachment
        )
        add_attachment_btn.grid(row=0, column=1, padx=12, pady=8, sticky="e")
        
        self.attachments_frame = ctk.CTkFrame(
            attachments_frame,
            fg_color="transparent"
        )
        self.attachments_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        
        #   FOOTER  
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=35)
        footer_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        self.word_count_label = ctk.CTkLabel(
            footer_frame,
            text="Số từ: 0 | Ký tự: 0",
            font=("Arial", 10),
            text_color=self.COLORS['text_secondary']
        )
        self.word_count_label.pack(side="left")
        
        self.save_status_label = ctk.CTkLabel(
            footer_frame,
            text="",
            font=("Arial", 10),
            text_color=self.COLORS['secondary']
        )
        self.save_status_label.pack(side="right")
        
        self.show_empty_state()
    
    def close_detail(self):
        if self.on_close:
            self.on_close()
    
    def display_note(self, note: Dict):
        self.current_note = note
        
        if hasattr(self, 'empty_label') and self.empty_label:
            self.empty_label.destroy()
            self.empty_label = None
        
        # Tiêu đề
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note.get('title', ''))
        
        # Nút quan trọng
        if note.get('is_starred'):
            self.star_btn.configure(
                fg_color=self.COLORS['secondary'],
                text_color="white"
            )
        else:
            self.star_btn.configure(
                fg_color="transparent",
                text_color=self.COLORS['secondary']
            )
        
        # Danh mục và ưu tiên
        category_map = {
            "General": "Chung",
            "Work": "Công việc",
            "Personal": "Cá nhân",
            "Ideas": "Ý tưởng",
            "Tasks": "Nhiệm vụ",
            "Study": "Học tập"
        }
        priority_map = {
            "low": "Thấp",
            "medium": "Trung bình",
            "high": "Cao",
            "urgent": "Khẩn cấp"
        }
        
        category_en = note.get('category', 'General')
        priority_en = note.get('priority', 'medium')
        
        self.category_var.set(category_map.get(category_en, category_en))
        self.priority_var.set(priority_map.get(priority_en, priority_en))
        
        # Ngày tạo
        created = note.get('created_date')
        updated = note.get('updated_date')
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        if isinstance(updated, str):
            updated = datetime.fromisoformat(updated)
        
        date_text = f"Tạo: {created.strftime('%d/%m/%Y %H:%M')}"
        if updated:
            date_text += f" | Cập nhật: {updated.strftime('%d/%m/%Y %H:%M')}"
        self.date_label.configure(text=date_text)
        
        # Nội dung
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", note.get('content', ''))
        
        # Tags
        tags = note.get('tags', [])
        self.tags_entry.delete(0, "end")
        if tags:
            self.tags_entry.insert(0, ", ".join(tags))
        
        # Hiển thị ngày đến hạn
        due_date = note.get('due_date')
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                formatted_due_date = due_date_obj.strftime('%d/%m/%Y')
                self.due_date_label.configure(
                    text=formatted_due_date,
                    text_color=self.COLORS['text_primary']
                )
                self.clear_due_date_btn.pack(side="left", padx=2)  # Hiện nút xóa
            except:
                self.due_date_label.configure(text="Lỗi định dạng")
                self.clear_due_date_btn.pack_forget()
        else:
            self.due_date_label.configure(text="Không có")
            self.clear_due_date_btn.pack_forget()  # Ẩn nút xóa
        
        # Hiển thị nhắc hẹn
        reminder = note.get('reminder_datetime')
        if reminder:
            try:
                reminder_obj = datetime.fromisoformat(reminder)
                formatted_reminder = reminder_obj.strftime('%d/%m/%Y %H:%M')
                self.reminder_label.configure(
                    text=formatted_reminder,
                    text_color=self.COLORS['text_primary']
                )
                self.clear_reminder_btn.pack(side="left", padx=2)  # Hiện nút xóa
                
                # Đổi màu nếu sắp đến hạn (trong vòng 24h)
                time_diff = reminder_obj - datetime.now()
                if time_diff.total_seconds() <= 86400:  # 24 giờ
                    self.reminder_label.configure(text_color="#DC2626")
            except:
                self.reminder_label.configure(text="Lỗi định dạng")
                self.clear_reminder_btn.pack_forget()
        else:
            self.reminder_label.configure(text="Không có")
            self.clear_reminder_btn.pack_forget()  # Ẩn nút xóa
        
        # Tệp đính kèm
        self.display_attachments(note.get('attachment_list', []))
        self.update_word_count()
        
        logger.info(f"Hiển thị ghi chú: {note['_id']}")
    
    def display_attachments(self, attachments: list):
        for widget in self.attachments_frame.winfo_children():
            widget.destroy()
        
        if not attachments:
            no_attach_label = ctk.CTkLabel(
                self.attachments_frame,
                text="Chưa có tệp đính kèm",
                font=("Arial", 10),
                text_color=self.COLORS['text_secondary']
            )
            no_attach_label.pack(pady=8)
            return
        
        for attachment in attachments:
            attach_item = ctk.CTkFrame(
                self.attachments_frame,
                fg_color="white",
                corner_radius=6,
                border_width=1,
                border_color=self.COLORS['border']
            )
            attach_item.pack(fill="x", pady=4)
            
            file_type = attachment.get('filetype', '').lower()
            filename = attachment.get('filename', 'Unknown')
            filepath = attachment.get('filepath', '')
            attachment_id = attachment.get('_id')
            
            # Thông tin file
            info_frame = ctk.CTkFrame(attach_item, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=6)
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=filename,
                font=("Arial", 11),
                anchor="w",
                text_color=self.COLORS['text_primary']
            )
            name_label.pack(anchor="w")
            
            filesize = attachment.get('filesize', 0)
            size_text = self.format_file_size(filesize)
            size_label = ctk.CTkLabel(
                info_frame,
                text=size_text,
                font=("Arial", 9),
                text_color=self.COLORS['text_secondary'],
                anchor="w"
            )
            size_label.pack(anchor="w")
            
            # Nút hành động
            action_frame = ctk.CTkFrame(attach_item, fg_color="transparent")
            action_frame.pack(side="right", padx=8)
            
            # Nút xem (nếu là ảnh)
            if file_type in ['.jpg', '.jpeg', '.png', '.gif'] and os.path.exists(filepath):
                view_btn = ctk.CTkButton(
                    action_frame,
                    text="Xem",
                    width=55,
                    height=26,
                    font=("Arial", 10),
                    fg_color="transparent",
                    hover_color=self.COLORS['bg_hover'],
                    text_color=self.COLORS['secondary'],
                    border_width=1,
                    border_color=self.COLORS['secondary'],
                    command=lambda fp=filepath, fn=filename: self.preview_image(fp, fn)
                )
                view_btn.pack(side="left", padx=2)
            
            delete_btn = ctk.CTkButton(
                action_frame,
                text="Xóa",
                width=55,
                height=26,
                font=("Arial", 10),
                fg_color="transparent",
                hover_color="#fee2e2",
                text_color=self.COLORS['danger'],
                border_width=1,
                border_color=self.COLORS['danger'],
                command=lambda aid=attachment_id: self.delete_attachment(aid)
            )
            delete_btn.pack(side="left", padx=2)
    
    def preview_image(self, filepath: str, filename: str):
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        
        # TẠO TOPLEVEL - LUÔN HIỆN TRÊN CÙNG
        self.preview_window = ctk.CTkToplevel(self.master.master)  # master.master để lên trên app
        self.preview_window.title(f"Xem ảnh: {filename}")
        self.preview_window.geometry("800x600")
        self.preview_window.configure(fg_color=self.COLORS['bg_main'])
        
        # ĐẶT TRÊN CÙNG
        self.preview_window.attributes('-topmost', True)
        self.preview_window.transient(self.master.master)
        self.preview_window.grab_set()
        
        # CENTER WINDOW
        self.preview_window.update_idletasks()
        x = (self.preview_window.winfo_screenwidth() - 800) // 2
        y = (self.preview_window.winfo_screenheight() - 600) // 2
        self.preview_window.geometry(f"800x600+{x}+{y}")
        
        try:
            # Load và resize ảnh
            image = Image.open(filepath)
            
            max_width, max_height = 750, 500
            img_width, img_height = image.size
            
            ratio = min(max_width/img_width, max_height/img_height)
            new_size = (int(img_width * ratio), int(img_height * ratio))
            
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Hiển thị ảnh
            img_label = ctk.CTkLabel(
                self.preview_window,
                image=photo,
                text=""
            )
            img_label.image = photo  # Giữ reference
            img_label.pack(expand=True, pady=20)
            
            # Nút đóng
            close_btn = ctk.CTkButton(
                self.preview_window,
                text="Đóng",
                width=100,
                fg_color=self.COLORS['secondary'],
                hover_color=self.COLORS['primary'],
                command=self.preview_window.destroy
            )
            close_btn.pack(pady=10)
            
        except Exception as e:
            logger.error(f"Lỗi preview ảnh: {str(e)}")
            ctk.CTkLabel(
                self.preview_window,
                text=f"Không thể hiển thị ảnh\n{str(e)}",
                text_color=self.COLORS['danger']
            ).pack(expand=True)
    
    def delete_attachment(self, attachment_id: str):
        if self.current_note:
            self.on_attachment_delete(self.current_note['_id'], attachment_id)
    
    def delete_note(self):
        if self.current_note:
            # Gọi callback từ main app để xử lý xóa
            from tkinter import messagebox
            result = messagebox.askyesno(
                "Xác nhận xóa",
                "Bạn có chắc chắn muốn xóa ghi chú này không?"
            )
            if result:
                # Import controller để xóa trực tiếp
                if hasattr(self.master.master, 'on_note_delete'):
                    self.master.master.on_note_delete(self.current_note['_id'])
    
    def format_file_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} GB"
    
    def save_title(self, event=None):
        if not self.current_note:
            return
        
        new_title = self.title_entry.get().strip()
        if new_title and new_title != self.current_note.get('title'):
            self.on_update(self.current_note['_id'], title=new_title)
            self.show_save_status("Đã lưu tiêu đề")
    
    def auto_save_content(self, event=None):
        if not self.current_note:
            return
        
        self.update_word_count()
        
        if hasattr(self, 'save_timer'):
            self.after_cancel(self.save_timer)
        
        self.save_timer = self.after(1000, self.save_content)
    
    def save_content(self):
        if not self.current_note:
            return
        
        new_content = self.content_text.get("1.0", "end-1c")
        if new_content != self.current_note.get('content'):
            self.on_update(self.current_note['_id'], content=new_content)
            self.show_save_status("Đã lưu")
    
    def update_category(self, value):
        if not self.current_note:
            return
        
        category_reverse_map = {
            "Chung": "General",
            "Công việc": "Work",
            "Cá nhân": "Personal",
            "Ý tưởng": "Ideas",
            "Nhiệm vụ": "Tasks",
            "Học tập": "Study"
        }
        
        category_en = category_reverse_map.get(value, value)
        self.on_update(self.current_note['_id'], category=category_en)
    
    def update_priority(self, value):
        if not self.current_note:
            return
        
        priority_reverse_map = {
            "Thấp": "low",
            "Trung bình": "medium",
            "Cao": "high",
            "Khẩn cấp": "urgent"
        }
        
        priority_en = priority_reverse_map.get(value, value)
        self.on_update(self.current_note['_id'], priority=priority_en)
    
    def update_tags(self, event=None):
        if not self.current_note:
            return
        
        tags_text = self.tags_entry.get().strip()
        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        self.on_update(self.current_note['_id'], tags=tags)
        self.show_save_status("Đã cập nhật nhãn")
    
    def toggle_star(self):
        if self.current_note:
            self.on_update(
                self.current_note['_id'],
                is_starred=not self.current_note.get('is_starred', False)
            )
    
    def archive_note(self):
        if self.current_note:
            self.on_update(
                self.current_note['_id'],
                is_archived=not self.current_note.get('is_archived', False)
            )
    
    def add_attachment(self):
        if not self.current_note:
            return
        
        file_path = filedialog.askopenfilename(
            title="Chọn tệp",
            filetypes=[
                ("Tất cả", "*.*"),
                ("Hình ảnh", "*.png *.jpg *.jpeg *.gif"),
                ("Tài liệu", "*.pdf *.doc *.docx"),
                ("Bảng tính", "*.xls *.xlsx")
            ]
        )
        
        if file_path:
            self.on_attachment_add(self.current_note['_id'], file_path)
    
    def update_word_count(self):
        content = self.content_text.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        
        self.word_count_label.configure(text=f"Số từ: {words} | Ký tự: {chars}")
    
    def show_save_status(self, message: str):
        self.save_status_label.configure(text=message)
        self.after(2000, lambda: self.save_status_label.configure(text=""))
    
    def show_empty_state(self):
        self.empty_label = ctk.CTkLabel(
            self,
            text="\n\nChọn một ghi chú để xem chi tiết\n\nhoặc tạo ghi chú mới",
            font=("Arial", 14),
            text_color=self.COLORS['text_secondary'],
            justify="center"
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def clear(self):
        self.current_note = None
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        self.tags_entry.delete(0, "end")
        self.due_date_label.configure(text="Không có")
        self.reminder_label.configure(text="Không có")
        self.clear_due_date_btn.pack_forget()
        self.clear_reminder_btn.pack_forget()
        self.show_empty_state()
    def manage_reminder(self):
        if not self.current_note:
            return
        
        # Tạo popup chọn thời gian nhắc
        self.reminder_window = ctk.CTkToplevel(self)
        self.reminder_window.title("Đặt nhắc hẹn")
        self.reminder_window.geometry("350x200")
        self.reminder_window.configure(fg_color=self.COLORS['bg_surface'])
        self.reminder_window.attributes('-topmost', True)
        self.reminder_window.transient(self)
        self.reminder_window.grab_set()
        
        # Center window
        self.reminder_window.update_idletasks()
        x = (self.reminder_window.winfo_screenwidth() - 350) // 2
        y = (self.reminder_window.winfo_screenheight() - 200) // 2
        self.reminder_window.geometry(f"350x200+{x}+{y}")
        
        # Ngày nhắc
        ctk.CTkLabel(
            self.reminder_window,
            text="Ngày nhắc:",
            font=("Arial", 12)
        ).pack(pady=(15, 5))
        
        self.reminder_date_var = ctk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        if self.current_note.get('reminder_datetime'):
            reminder_date = self.current_note['reminder_datetime'].split('T')[0]
            self.reminder_date_var.set(reminder_date)
        
        reminder_date_entry = ctk.CTkEntry(
            self.reminder_window,
            textvariable=self.reminder_date_var,
            width=120
        )
        reminder_date_entry.pack(pady=5)
        
        # Giờ nhắc
        ctk.CTkLabel(
            self.reminder_window,
            text="Giờ nhắc (HH:MM):",
            font=("Arial", 12)
        ).pack(pady=(10, 5))
        
        self.reminder_time_var = ctk.StringVar(value="09:00")
        if self.current_note.get('reminder_datetime'):
            reminder_time = self.current_note['reminder_datetime'].split('T')[1][:5]
            self.reminder_time_var.set(reminder_time)
        
        reminder_time_entry = ctk.CTkEntry(
            self.reminder_window,
            textvariable=self.reminder_time_var,
            width=80
        )
        reminder_time_entry.pack(pady=5)
    
        # Nút xác nhận
        def confirm_reminder():
            date_str = self.reminder_date_var.get().strip()
            time_str = self.reminder_time_var.get().strip()
            
            if self.validate_date(date_str) and self.validate_time(time_str):
                reminder_datetime = f"{date_str}T{time_str}:00"
                self.on_update(self.current_note['_id'], reminder_datetime=reminder_datetime)
                self.reminder_window.destroy()
                self.show_save_status("Đã đặt nhắc hẹn")
            else:
                from tkinter import messagebox
                messagebox.showerror("Lỗi", "Định dạng ngày/giờ không hợp lệ")
        
        confirm_btn = ctk.CTkButton(
            self.reminder_window,
            text="Xác nhận",
            command=confirm_reminder
        )
        confirm_btn.pack(pady=15)

    def validate_time(self, time_string):
        try:
            datetime.strptime(time_string, '%H:%M')
            return True
        except ValueError:
            return False

    def clear_reminder(self):
        if self.current_note:
            self.on_update(self.current_note['_id'], reminder_datetime=None)
            self.show_save_status("Đã xóa nhắc hẹn")
    
    def manage_due_date(self):
        if not self.current_note:
            return
        
        # Tạo popup chọn ngày
        self.due_date_window = ctk.CTkToplevel(self)
        self.due_date_window.title("Đặt ngày đến hạn")
        self.due_date_window.geometry("300x150")
        self.due_date_window.configure(fg_color=self.COLORS['bg_surface'])
        self.due_date_window.attributes('-topmost', True)
        self.due_date_window.transient(self)
        self.due_date_window.grab_set()
        
        # Center window
        self.due_date_window.update_idletasks()
        x = (self.due_date_window.winfo_screenwidth() - 300) // 2
        y = (self.due_date_window.winfo_screenheight() - 150) // 2
        self.due_date_window.geometry(f"300x150+{x}+{y}")
        
        # Widget chọn ngày
        ctk.CTkLabel(
            self.due_date_window,
            text="Chọn ngày đến hạn:",
            font=("Arial", 12)
        ).pack(pady=10)
        
        # Lấy ngày hiện tại
        current_date = datetime.now().strftime('%Y-%m-%d')
        if self.current_note.get('due_date'):
            current_date = self.current_note['due_date']
        
        due_date_entry = ctk.CTkEntry(
            self.due_date_window,
            placeholder_text="YYYY-MM-DD",
            width=120
        )
        due_date_entry.insert(0, current_date)
        due_date_entry.pack(pady=5)
        
        # Nút xác nhận
        def confirm_due_date():
            due_date = due_date_entry.get().strip()
            if self.validate_date(due_date):
                self.on_update(self.current_note['_id'], due_date=due_date)
                self.due_date_window.destroy()
                self.show_save_status("Đã cập nhật hạn")
            else:
                from tkinter import messagebox
                messagebox.showerror("Lỗi", "Định dạng ngày không hợp lệ. Dùng YYYY-MM-DD")
        
        confirm_btn = ctk.CTkButton(
            self.due_date_window,
            text="Xác nhận",
            command=confirm_due_date
        )
        confirm_btn.pack(pady=10)

    def validate_date(self, date_string):
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def clear_due_date(self):
        if self.current_note:
            self.on_update(self.current_note['_id'], due_date=None)
            self.show_save_status("Đã xóa hạn")