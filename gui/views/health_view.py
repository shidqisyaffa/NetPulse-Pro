"""
gui/views/health_view.py
========================
Panel tampilan untuk modul Smart Health Check.
Menampilkan daftar IP, memulai ping paralel, dan
menampilkan status Online (hijau) / Offline (merah) per IP.
"""

import threading
import customtkinter as ctk

from gui.theme import COLORS, FONTS, PADDING_MD, PADDING_SM, PADDING_LG
from gui.widgets import (
    ModuleCard, PrimaryButton, SecondaryButton, StyledEntry,
    LogArea, SectionLabel, ProgressSection
)
from core.health_check import run_health_check


class HealthView(ctk.CTkFrame):
    """
    View untuk modul Smart Health Check.
    User bisa memasukkan IP secara manual atau
    langsung menggunakan IP dari hasil Subdomain Recon.
    """

    def __init__(self, parent, shared_log=None, get_recon_ips=None):
        """
        Args:
            parent        : Parent widget
            shared_log    : LogArea global (opsional)
            get_recon_ips : Fungsi yang mengembalikan list IP dari ReconView
        """
        super().__init__(parent, fg_color="transparent")
        self._shared_log = shared_log
        self._get_recon_ips = get_recon_ips
        self._results = []
        self._build_ui()

    # ---------------------------------------------------------------
    # Pembangunan UI
    # ---------------------------------------------------------------
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === Header ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING_LG, pady=(PADDING_LG, 0))

        ctk.CTkLabel(
            header, text="💓  Smart Health Check",
            font=FONTS["title"], text_color=COLORS["text_primary"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Ping paralel ke semua IP yang ditemukan — indikator Online/Offline real-time",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        # === Input IP ===
        input_card = ModuleCard(self, title="Daftar IP Target")
        input_card.grid(row=1, column=0, sticky="ew", padx=PADDING_LG, pady=PADDING_MD)

        # Textbox untuk input IP (satu per baris)
        self._ip_textbox = ctk.CTkTextbox(
            input_card,
            height=90,
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["accent_cyan"],
            font=FONTS["mono"],
            corner_radius=8,
            border_color=COLORS["border"],
            border_width=1,
        )
        self._ip_textbox.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_SM))
        self._ip_textbox.insert("end", "8.8.8.8\n1.1.1.1\n")

        hint = ctk.CTkLabel(
            input_card,
            text="💡  Masukkan satu IP per baris. Atau gunakan tombol 'Import dari Recon' untuk auto-fill.",
            font=FONTS["small"], text_color=COLORS["text_muted"]
        )
        hint.pack(anchor="w", padx=PADDING_MD, pady=(0, PADDING_SM))

        # Tombol aksi
        btn_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_MD))

        self._run_btn = PrimaryButton(btn_frame, "💓  Mulai Health Check", command=self._start_check)
        self._run_btn.pack(side="left", padx=(0, PADDING_SM))

        import_btn = SecondaryButton(btn_frame, "📥  Import dari Recon", command=self._import_from_recon)
        import_btn.pack(side="left", padx=(0, PADDING_SM))

        clear_btn = SecondaryButton(btn_frame, "🗑  Bersihkan", command=self._clear_input)
        clear_btn.pack(side="left")

        # Progress
        self._progress = ProgressSection(input_card, label="Progres Ping")
        self._progress.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_MD))

        # === Hasil Ping — Scrollable ===
        result_card = ModuleCard(self, title="Status Host")
        result_card.grid(row=2, column=0, sticky="nsew", padx=PADDING_LG, pady=PADDING_SM)

        self._scroll_frame = ctk.CTkScrollableFrame(
            result_card,
            fg_color=COLORS["bg_dark"],
            corner_radius=8,
        )
        self._scroll_frame.pack(fill="both", expand=True, padx=PADDING_MD, pady=(0, PADDING_MD))

        self._empty_label = ctk.CTkLabel(
            self._scroll_frame,
            text="Jalankan health check untuk melihat status host...",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        )
        self._empty_label.pack(pady=30)

        # Statistik
        stats_row = ctk.CTkFrame(result_card, fg_color="transparent")
        stats_row.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_SM))

        self._stat_online = ctk.CTkLabel(
            stats_row, text="🟢 Online: —",
            font=FONTS["label"], text_color=COLORS["accent_green"]
        )
        self._stat_online.pack(side="left", padx=(0, PADDING_LG))

        self._stat_offline = ctk.CTkLabel(
            stats_row, text="🔴 Offline: —",
            font=FONTS["label"], text_color=COLORS["accent_red"]
        )
        self._stat_offline.pack(side="left")

        # === Log ===
        log_card = ModuleCard(self, title="Log Proses")
        log_card.grid(row=3, column=0, sticky="ew", padx=PADDING_LG, pady=(PADDING_SM, PADDING_LG))
        self._log = LogArea(log_card, height=110)
        self._log.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_MD))

    # ---------------------------------------------------------------
    # Aksi Tombol
    # ---------------------------------------------------------------
    def _import_from_recon(self):
        """Import IP dari hasil Subdomain Recon secara otomatis."""
        if not self._get_recon_ips:
            self._log.append("⚠ Tidak ada koneksi ke modul Recon.")
            return

        ip_list = self._get_recon_ips()
        if not ip_list:
            self._log.append("⚠ Belum ada hasil dari modul Subdomain Recon.")
            return

        self._ip_textbox.delete("1.0", "end")
        for ip in ip_list:
            self._ip_textbox.insert("end", ip + "\n")

        self._log.append(f"✓ {len(ip_list)} IP berhasil diimport dari hasil Recon.")

    def _clear_input(self):
        self._ip_textbox.delete("1.0", "end")

    def _get_ip_list(self) -> list[str]:
        """Ambil dan parse daftar IP dari textbox."""
        raw = self._ip_textbox.get("1.0", "end").strip()
        ips = [line.strip() for line in raw.splitlines() if line.strip()]
        return ips

    def _start_check(self):
        ip_list = self._get_ip_list()
        if not ip_list:
            self._log.append("⚠ Masukkan setidaknya satu IP.")
            return

        self._run_btn.configure(state="disabled", text="⏳ Melakukan ping...")
        self._log.clear()
        self._progress.reset()
        self._clear_results()

        threading.Thread(
            target=self._run_in_background,
            args=(ip_list,),
            daemon=True
        ).start()

    def _clear_results(self):
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(
            self._scroll_frame,
            text="Melakukan ping...",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        ).pack(pady=30)

    # ---------------------------------------------------------------
    # Logika Health Check
    # ---------------------------------------------------------------
    def _run_in_background(self, ip_list: list):
        def log_cb(msg):
            self.after(0, self._log.append, msg)
            if self._shared_log:
                self.after(0, self._shared_log.append, msg)

        def progress_cb(current, total):
            self.after(0, self._progress.set_progress, current, total)

        try:
            results = run_health_check(
                ip_list=ip_list,
                log_callback=log_cb,
                progress_callback=progress_cb,
            )
            self._results = results
            self.after(0, self._show_results, results)
        except Exception as exc:
            self.after(0, self._log.append, f"❌ Error: {exc}")
        finally:
            self.after(0, self._run_btn.configure, {
                "state": "normal", "text": "💓  Mulai Health Check"
            })

    def _show_results(self, results: list):
        """Tampilkan hasil ping dengan indikator warna Online/Offline."""
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()

        if not results:
            ctk.CTkLabel(
                self._scroll_frame,
                text="Tidak ada hasil.", font=FONTS["body"],
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        online_count  = sum(1 for r in results if r["online"])
        offline_count = len(results) - online_count

        self._stat_online.configure(text=f"🟢 Online: {online_count}")
        self._stat_offline.configure(text=f"🔴 Offline: {offline_count}")

        # Header
        hdr = ctk.CTkFrame(self._scroll_frame, fg_color=COLORS["bg_light"], corner_radius=6)
        hdr.pack(fill="x", pady=(0, 4), padx=4)
        hdr.grid_columnconfigure((0, 1, 2), weight=1)
        for col, txt in enumerate(["IP Address", "Status", "Detail"]):
            ctk.CTkLabel(
                hdr, text=txt, font=FONTS["label"],
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=col, padx=10, pady=6, sticky="w")

        # Baris per IP
        for i, r in enumerate(results):
            row_color = COLORS["bg_medium"] if i % 2 == 0 else COLORS["bg_dark"]
            row = ctk.CTkFrame(self._scroll_frame, fg_color=row_color, corner_radius=4)
            row.pack(fill="x", pady=1, padx=4)
            row.grid_columnconfigure((0, 1, 2), weight=1)

            # IP
            ctk.CTkLabel(
                row, text=r["ip"],
                font=FONTS["mono"], text_color=COLORS["accent_cyan"]
            ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

            # Status badge (warna berbeda)
            if r["online"]:
                dot_color = COLORS["accent_green"]
                status_text = "● ONLINE"
            else:
                dot_color = COLORS["accent_red"]
                status_text = "● OFFLINE"

            ctk.CTkLabel(
                row, text=status_text,
                font=FONTS["label"], text_color=dot_color
            ).grid(row=0, column=1, padx=10, pady=8, sticky="w")

            # Detail RTT / message
            ctk.CTkLabel(
                row, text=r.get("message", "—"),
                font=FONTS["small"], text_color=COLORS["text_secondary"]
            ).grid(row=0, column=2, padx=10, pady=8, sticky="w")

    def get_results(self) -> list:
        return self._results

    def get_recon_ips_from_results(self) -> list[str]:
        """
        Helper: ekstrak IP dari hasil Recon untuk diimport.
        Dipanggil dari app.py melalui get_recon_ips callback.
        """
        return []
