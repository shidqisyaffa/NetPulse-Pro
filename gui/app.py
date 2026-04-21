"""
gui/app.py
==========
Kelas utama aplikasi NetPulse Pro.
Mengatur layout utama: Sidebar + Content Area + Global Log Bar.
Mengelola navigasi antar panel dan state data global.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

from gui.theme import (
    COLORS, FONTS, SIDEBAR_WIDTH,
    PADDING_MD, PADDING_SM, PADDING_LG,
    NAV_ICONS,
)
from gui.widgets import LogArea, PrimaryButton, SecondaryButton
from gui.views.dashboard_view  import DashboardView
from gui.views.benchmark_view  import BenchmarkView
from gui.views.doh_view        import DohView
from gui.views.recon_view      import ReconView
from gui.views.health_view     import HealthView
from core.reporter import export_report


# ═══════════════════════════════════════════════════════════════════════
# NetPulseApp — Root Application Window
# ═══════════════════════════════════════════════════════════════════════
class NetPulseApp(ctk.CTk):
    """
    Window utama NetPulse Pro.
    Layout:
        ┌──────────┬──────────────────────────────┐
        │ Sidebar  │       Content Frame           │
        │ (nav)    │                              │
        │          │                              │
        ├──────────┴──────────────────────────────┤
        │          Global Log Area                │
        └─────────────────────────────────────────┘
    """

    # Daftar panel navigasi
    PAGES = ["Dashboard", "DNS Benchmark", "DNS Traveler", "Subdomain Recon", "Health Check"]

    def __init__(self):
        super().__init__()

        # ── Konfigurasi Window ──────────────────────────────────────
        self.title("⚡ NetPulse Pro — Network & DNS Diagnostic Tool")
        self.geometry("1200x780")
        self.minsize(900, 600)
        self.configure(fg_color=COLORS["bg_dark"])

        # customtkinter: selalu gunakan dark mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── State ──────────────────────────────────────────────────
        self._active_page   = None
        self._nav_buttons   = {}    # name → CTkButton
        self._page_frames   = {}    # name → Frame widget

        # ── Build Layout ───────────────────────────────────────────
        self._build_layout()
        self._build_sidebar()
        self._build_content_area()
        self._build_global_log()
        self._build_views()

        # Tampilkan halaman awal
        self._navigate_to("Dashboard")

    # ---------------------------------------------------------------
    # Layout Utama
    # ---------------------------------------------------------------
    def _build_layout(self):
        """Konfigurasi grid utama window."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self):
        """
        Membangun sidebar di sisi kiri.
        Berisi logo, tombol navigasi, dan tombol export.
        """
        self._sidebar = ctk.CTkFrame(
            self,
            width=SIDEBAR_WIDTH,
            fg_color=COLORS["bg_sidebar"],
            corner_radius=0,
        )
        self._sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self._sidebar.grid_propagate(False)  # Kunci lebar sidebar

        # ── Logo ──
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=PADDING_MD, pady=PADDING_LG)

        ctk.CTkLabel(
            logo_frame, text="⚡",
            font=("Segoe UI Emoji", 28),
            text_color=COLORS["accent_blue"],
        ).pack(side="left")

        ctk.CTkLabel(
            logo_frame, text=" NetPulse\nPro",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_primary"],
            justify="left",
        ).pack(side="left", padx=(4, 0))

        # Garis pemisah
        ctk.CTkFrame(self._sidebar, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=PADDING_MD, pady=PADDING_SM
        )

        # ── Label Navigasi ──
        ctk.CTkLabel(
            self._sidebar, text="NAVIGASI",
            font=("Segoe UI", 9, "bold"),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=PADDING_MD, pady=(PADDING_MD, PADDING_SM))

        # ── Tombol Nav ──
        for page in self.PAGES:
            icon = NAV_ICONS.get(page, "•")
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"  {icon}  {page}",
                anchor="w",
                fg_color="transparent",
                hover_color=COLORS["bg_light"],
                text_color=COLORS["text_secondary"],
                font=FONTS["body"],
                height=40,
                corner_radius=8,
                command=lambda p=page: self._navigate_to(p),
            )
            btn.pack(fill="x", padx=PADDING_SM, pady=2)
            self._nav_buttons[page] = btn

        # ── Spacer ──
        ctk.CTkFrame(self._sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Garis pemisah bawah
        ctk.CTkFrame(self._sidebar, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=PADDING_MD, pady=PADDING_SM
        )

        # ── Tombol Export ──
        export_btn = ctk.CTkButton(
            self._sidebar,
            text="💾  Export Laporan",
            fg_color=COLORS["accent_purple"],
            hover_color="#7142D0",
            text_color="#FFFFFF",
            font=FONTS["label"],
            height=38,
            corner_radius=8,
            command=self._export_report,
        )
        export_btn.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_SM))

        # ── Version info ──
        ctk.CTkLabel(
            self._sidebar,
            text="v1.0.0 • Tugas Pemrograman Jaringan",
            font=FONTS["mono_sm"],
            text_color=COLORS["text_muted"],
        ).pack(pady=(0, PADDING_MD))

    def _build_content_area(self):
        """Membangun area konten di sebelah kanan sidebar."""
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

    def _build_global_log(self):
        """
        Membangun area log global di bagian bawah.
        Menampilkan semua aktivitas dari semua modul.
        """
        log_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_darkest"],
            corner_radius=0,
            height=130,
            border_width=1,
            border_color=COLORS["border"],
        )
        log_frame.grid(row=1, column=1, sticky="ew")
        log_frame.pack_propagate(False)

        header_row = ctk.CTkFrame(log_frame, fg_color="transparent")
        header_row.pack(fill="x", padx=PADDING_MD, pady=(PADDING_SM, 0))

        ctk.CTkLabel(
            header_row, text="📋  Activity Log",
            font=FONTS["label"], text_color=COLORS["text_secondary"],
        ).pack(side="left")

        # Tombol bersihkan log
        ctk.CTkButton(
            header_row,
            text="Bersihkan",
            font=FONTS["small"],
            fg_color="transparent",
            hover_color=COLORS["bg_light"],
            text_color=COLORS["text_muted"],
            border_color=COLORS["border"],
            border_width=1,
            height=24,
            width=80,
            corner_radius=6,
            command=self._clear_global_log,
        ).pack(side="right")

        self._global_log = LogArea(log_frame, height=90)
        self._global_log.pack(fill="x", padx=PADDING_MD, pady=PADDING_SM)
        self._global_log.append("✅ NetPulse Pro siap digunakan. Pilih modul di sidebar kiri.")

    # ---------------------------------------------------------------
    # Build Semua View
    # ---------------------------------------------------------------
    def _build_views(self):
        """
        Membuat instance semua view/panel dan menempatkannya
        di content area (semua tersembunyi dulu).
        """
        # Scrollable wrapper untuk setiap view
        def _make_scroll(cls, **kwargs):
            scroll = ctk.CTkScrollableFrame(
                self._content,
                fg_color="transparent",
                scrollbar_button_color=COLORS["bg_light"],
                scrollbar_button_hover_color=COLORS["accent_blue"],
            )
            view = cls(scroll, shared_log=self._global_log, **kwargs)
            view.pack(fill="both", expand=True)
            return scroll, view

        # Dashboard (tidak perlu scroll)
        dashboard_frame = DashboardView(
            self._content,
            navigate_to=self._navigate_to,
        )
        self._page_frames["Dashboard"] = dashboard_frame

        # DNS Benchmark
        bm_scroll, self._bm_view = _make_scroll(BenchmarkView)
        self._page_frames["DNS Benchmark"] = bm_scroll

        # DoH Traveler
        doh_scroll, self._doh_view = _make_scroll(DohView)
        self._page_frames["DNS Traveler"] = doh_scroll

        # Subdomain Recon
        recon_scroll, self._recon_view = _make_scroll(ReconView)
        self._page_frames["Subdomain Recon"] = recon_scroll

        # Health Check — dengan callback ke hasil Recon
        hc_scroll, self._hc_view = _make_scroll(
            HealthView,
            get_recon_ips=self._get_recon_ips,
        )
        self._page_frames["Health Check"] = hc_scroll

        # Sembunyikan semua view
        for frame in self._page_frames.values():
            frame.grid_forget()

    # ---------------------------------------------------------------
    # Navigasi
    # ---------------------------------------------------------------
    def _navigate_to(self, page_name: str):
        """
        Berpindah ke panel yang dipilih.
        Menyembunyikan panel saat ini dan menampilkan yang baru.
        """
        if self._active_page == page_name:
            return

        # Sembunyikan semua panel
        for frame in self._page_frames.values():
            frame.grid_forget()

        # Reset style semua tombol nav
        for name, btn in self._nav_buttons.items():
            btn.configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
            )

        # Tampilkan panel yang dipilih
        frame = self._page_frames.get(page_name)
        if frame:
            frame.grid(row=0, column=0, sticky="nsew")

        # Aktifkan tombol nav yang dipilih
        if page_name in self._nav_buttons:
            self._nav_buttons[page_name].configure(
                fg_color=COLORS["bg_light"],
                text_color=COLORS["accent_blue"],
            )

        self._active_page = page_name

    # ---------------------------------------------------------------
    # Callback & Helpers
    # ---------------------------------------------------------------
    def _get_recon_ips(self) -> list[str]:
        """
        Mengambil semua IP dari hasil Subdomain Recon.
        Digunakan oleh Health Check untuk import IP otomatis.
        """
        results = self._recon_view.get_results()
        ips = []
        for item in results.get("found", []):
            ips.extend(item.get("addresses", []))
        return list(dict.fromkeys(ips))  # Deduplikasi, pertahankan urutan

    def _clear_global_log(self):
        """Membersihkan area log global."""
        self._global_log.clear()
        self._global_log.append("📋 Log dibersihkan.")

    def _export_report(self):
        """
        Membuka dialog file save dan mengexport laporan JSON.
        Mengumpulkan semua hasil dari setiap view.
        """
        # Dialog pilih lokasi simpan
        file_path = filedialog.asksaveasfilename(
            title="Simpan Laporan Diagnostik",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialfile="diagnostic_report.json",
        )

        if not file_path:
            return  # User membatalkan dialog

        self._global_log.append("📦 Mengekspor laporan...")

        try:
            saved_path = export_report(
                benchmark_results=self._bm_view.get_results(),
                doh_results=self._doh_view.get_results(),
                recon_results=self._recon_view.get_results(),
                health_results=self._hc_view.get_results(),
                output_path=file_path,
                log_callback=lambda msg: self.after(0, self._global_log.append, msg),
            )

            messagebox.showinfo(
                "Export Berhasil",
                f"Laporan berhasil disimpan ke:\n{saved_path}",
            )

        except Exception as exc:
            self._global_log.append(f"❌ Gagal mengekspor: {exc}")
            messagebox.showerror("Export Gagal", str(exc))
