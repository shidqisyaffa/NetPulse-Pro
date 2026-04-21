"""
gui/views/dashboard_view.py
============================
Panel Dashboard utama yang ditampilkan saat aplikasi pertama dibuka.
Menampilkan ringkasan fitur, status sistem, dan tombol akses cepat.
"""

import platform
import socket
import customtkinter as ctk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gui.theme import COLORS, FONTS, PADDING_MD, PADDING_SM, PADDING_LG


class DashboardView(ctk.CTkFrame):
    """
    Dashboard utama NetPulse Pro.
    Menampilkan kartu fitur, info sistem, dan animasi gradient header.
    """

    def __init__(self, parent, navigate_to=None):
        super().__init__(parent, fg_color="transparent")
        self._navigate_to = navigate_to  # Callback untuk pindah halaman
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # === Hero Banner ===
        hero = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_medium"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["accent_blue"],
        )
        hero.grid(row=0, column=0, sticky="ew", padx=PADDING_LG, pady=PADDING_LG)

        ctk.CTkLabel(
            hero,
            text="⚡  NetPulse Pro",
            font=("Segoe UI", 32, "bold"),
            text_color=COLORS["accent_blue"],
        ).pack(pady=(PADDING_LG, 4))

        ctk.CTkLabel(
            hero,
            text="Network & DNS Diagnostic Toolkit",
            font=FONTS["heading"],
            text_color=COLORS["text_secondary"],
        ).pack()

        ctk.CTkLabel(
            hero,
            text=(
                "Aplikasi diagnostik jaringan modern dengan 4 modul terintegrasi:\n"
                "DNS Benchmark  •  DoH Traveler  •  Subdomain Recon  •  Smart Health Check"
            ),
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
            justify="center",
        ).pack(pady=(4, PADDING_LG))

        # === Kartu Fitur (2x2 grid) ===
        features_frame = ctk.CTkFrame(self, fg_color="transparent")
        features_frame.grid(row=1, column=0, sticky="ew", padx=PADDING_LG, pady=0)
        features_frame.grid_columnconfigure((0, 1), weight=1, uniform="feat")

        feature_data = [
            {
                "icon": "📊",
                "title": "DNS Speed Benchmark",
                "desc": (
                    "Ukur latensi DNS Google, Cloudflare, OpenDNS,\n"
                    "dan Quad9 secara bersamaan dengan bar chart interaktif."
                ),
                "color": COLORS["accent_blue"],
                "nav": "DNS Benchmark",
            },
            {
                "icon": "🌐",
                "title": "DNS Traveler (DoH)",
                "desc": (
                    "Cek konsistensi IP domain melalui DNS-over-HTTPS\n"
                    "dari Google & Cloudflare. Deteksi DNS poisoning."
                ),
                "color": COLORS["accent_purple"],
                "nav": "DNS Traveler",
            },
            {
                "icon": "🔍",
                "title": "Subdomain Recon",
                "desc": (
                    "Scan subdomain umum secara multithreaded.\n"
                    "Optimalkan CPU multi-core untuk kecepatan maksimal."
                ),
                "color": COLORS["accent_cyan"],
                "nav": "Subdomain Recon",
            },
            {
                "icon": "💓",
                "title": "Smart Health Check",
                "desc": (
                    "Ping paralel ke semua IP yang ditemukan.\n"
                    "Indikator warna hijau/merah untuk Online/Offline."
                ),
                "color": COLORS["accent_green"],
                "nav": "Health Check",
            },
        ]

        for i, feat in enumerate(feature_data):
            row_idx, col_idx = divmod(i, 2)
            self._create_feature_card(
                features_frame, feat, row_idx, col_idx
            )

        # === Info Sistem ===
        sys_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_medium"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        sys_card.grid(row=2, column=0, sticky="ew", padx=PADDING_LG, pady=PADDING_MD)
        sys_card.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="sys")

        ctk.CTkLabel(
            sys_card, text="System Info",
            font=FONTS["subhead"], text_color=COLORS["text_secondary"]
        ).grid(row=0, column=0, columnspan=4, padx=PADDING_MD, pady=(PADDING_MD, PADDING_SM), sticky="w")

        sys_info = [
            ("OS", f"{platform.system()} {platform.release()}"),
            ("Hostname", socket.gethostname()),
            ("Python", platform.python_version()),
            ("Arch", platform.machine()),
        ]

        for col, (label, value) in enumerate(sys_info):
            item_frame = ctk.CTkFrame(sys_card, fg_color=COLORS["bg_dark"], corner_radius=8)
            item_frame.grid(row=1, column=col, padx=PADDING_SM, pady=(0, PADDING_MD), sticky="nsew")

            ctk.CTkLabel(
                item_frame, text=label,
                font=FONTS["small"], text_color=COLORS["text_muted"]
            ).pack(padx=10, pady=(8, 0))
            ctk.CTkLabel(
                item_frame, text=value,
                font=FONTS["label"], text_color=COLORS["text_primary"]
            ).pack(padx=10, pady=(0, 8))

    def _create_feature_card(self, parent, feat: dict, row: int, col: int):
        """Membuat satu kartu fitur yang dapat diklik."""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_medium"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            cursor="hand2",
        )
        card.grid(row=row, column=col, padx=PADDING_SM, pady=PADDING_SM, sticky="nsew")

        # Garis aksen warna di atas kartu
        accent_bar = ctk.CTkFrame(card, fg_color=feat["color"], height=3, corner_radius=0)
        accent_bar.pack(fill="x")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=PADDING_MD, pady=PADDING_MD)

        ctk.CTkLabel(
            content, text=feat["icon"],
            font=("Segoe UI Emoji", 28),
        ).pack(anchor="w")

        ctk.CTkLabel(
            content, text=feat["title"],
            font=FONTS["subhead"], text_color=feat["color"]
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            content, text=feat["desc"],
            font=FONTS["small"], text_color=COLORS["text_secondary"],
            justify="left", wraplength=320
        ).pack(anchor="w", pady=(4, 0))

        # Tombol navigate kecil
        nav_name = feat["nav"]
        btn = ctk.CTkButton(
            content,
            text=f"Buka {feat['title']} →",
            font=FONTS["small"],
            fg_color="transparent",
            hover_color=COLORS["bg_light"],
            text_color=feat["color"],
            border_color=feat["color"],
            border_width=1,
            height=28,
            corner_radius=6,
            command=lambda n=nav_name: self._navigate_to and self._navigate_to(n),
        )
        btn.pack(anchor="w", pady=(PADDING_MD, 0))
