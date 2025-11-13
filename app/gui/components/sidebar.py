from operator import iconcat

import customtkinter as ctk
from PIL import Image, ImageDraw


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_category_change, auto_select=True):
        super().__init__(parent, width=280, corner_radius=0, fg_color="#1e1e1e")

        self.on_category_change = on_category_change
        self.auto_select = auto_select





        # User info với avatar
        user_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        user_frame.pack(fill="x", padx=15, pady=(10, 5))
        user_frame.pack_propagate(False)

        # Avatar placeholder
        avatar_frame = ctk.CTkFrame(user_frame, width=40, height=40, corner_radius=20, fg_color="#4a4a4a")
        avatar_frame.pack(side="left", padx=(0, 10))
        avatar_frame.pack_propagate(False)

        # User email và dropdown icon
        email_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        email_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            email_frame,
            text="yirpng@gmail.com",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff",
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            email_frame,
            text="yirpng@gmail.com ⌄",
            font=("Segoe UI", 10),
            text_color="#8a8a8a",
            anchor="w"
        ).pack(anchor="w")

        search_frame = ctk.CTkFrame(self, fg_color="#2d2d2d", corner_radius=6, height=36)
        search_frame.pack(fill="x", padx=15, pady=(10, 20))
        search_frame.pack_propagate(False)

        # Icon kính lúp (dùng unicode hoặc ảnh)
        search_icon = ctk.CTkLabel(
            search_frame,
            text="🔍",  # hoặc dùng hình ảnh ở dưới nếu muốn icon thật
            text_color="#8a8a8a",
            font=("Segoe UI", 14),
            width=25
        )
        search_icon.pack(side="left", padx=(8, 0))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Tìm kiếm",
            height=36,
            border_width=0,
            corner_radius=0,
            fg_color="#2d2d2d",
            text_color="#ffffff",
            placeholder_text_color="#8a8a8a"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 8))

        # Categories với icons
        categories = [
            ("☀️", "Ngày của Tôi"),
            ("⭐", "Quan trọng"),
            ("📅", "Đã lập kế hoạch"),
            ("👤", "Đã giao cho tôi"),
            ("🏠", "Tác vụ"),
            ("👋", "Bắt đầu"),
            ("📋", "Cửa hàng tạp hóa"),
            ("☰", "Thử thách"),
        ]

        self.category_buttons = {}
        for item in categories:
            icon = item[0]
            name = item[1]
            badge = item[2] if len(item) > 2 else None

            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.pack(fill="x", padx=8, pady=1)

            btn = ctk.CTkButton(
                btn_frame,
                text=f"{icon}  {name}",
                anchor="w",
                fg_color="transparent",
                hover_color="#2d2d2d",
                text_color="#ffffff",
                height=40,
                font=("Segoe UI", 12),
                border_width=0,
                command=lambda n=name: self.select_category(n)
            )
            btn.pack(side="left", fill="both", expand=True)

            # Badge (số lượng task hoặc pin icon)
            if badge:
                badge_color = "#4a4a4a" if badge.isdigit() else "transparent"
                badge_label = ctk.CTkLabel(
                    btn_frame,
                    text=badge,
                    font=("Segoe UI", 11),
                    text_color="#ffffff",
                    fg_color=badge_color,
                    width=25,
                    height=25,
                    corner_radius=4
                )
                badge_label.pack(side="right", padx=(5, 10))

            self.category_buttons[name] = btn

        # Spacer
        ctk.CTkFrame(self, fg_color="transparent", height=20).pack(fill="x")

        # Bottom button
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        new_list_btn = ctk.CTkButton(
            bottom_frame,
            text="＋  Danh sách mới",
            anchor="w",
            fg_color="transparent",
            hover_color="#2d2d2d",
            text_color="#ffffff",
            height=40,
            font=("Segoe UI", 12),
            border_width=0
        )
        new_list_btn.pack(side="left", fill="x", expand=True)

        # Icon button (share/export)
        icon_btn = ctk.CTkButton(
            bottom_frame,
            text="⎘",
            width=40,
            fg_color="transparent",
            hover_color="#2d2d2d",
            text_color="#ffffff",
            font=("Segoe UI", 16)
        )
        icon_btn.pack(side="right", padx=(5, 0))

        # Auto-select default category
        if self.auto_select:
            self.select_category("Ngày của Tôi")

    def select_category(self, category):
        # Reset all buttons
        for name, btn in self.category_buttons.items():
            btn.configure(fg_color="transparent")

        # Highlight selected với viền trái màu xanh
        if category in self.category_buttons:
            self.category_buttons[category].configure(fg_color="#2d2d2d")

        # Callback
        self.on_category_change(category)