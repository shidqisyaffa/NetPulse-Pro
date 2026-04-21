"""
gui/views/recon_view.py
=======================
Panel tampilan untuk modul Multithreaded Subdomain Recon.
Menampilkan progress scan, tabel hasil subdomain,
dan indikator hijau/merah per subdomain yang ditemukan.
"""

import threading
import customtkinter as ctk

from gui.theme import COLORS, FONTS, PADDING_MD, PADDING_SM, PADDING_LG
from gui.widgets import (
    ModuleCard, PrimaryButton, StyledEntry,
    LogArea, SectionLabel, ProgressSection
)
from core.subdomain_recon import run_subdomain_recon, DEFAULT_SUBDOMAINS


class ReconView(ctk.CTkFrame):
    """
    View untuk modul Multithreaded Subdomain Reconnaissance.
    Menampilkan progres scan real-time dan daftar subdomain yang ditemukan.
    """

    def __init__(self, parent, shared_log=None):
        super().__init__(parent, fg_color="transparent")
        self._shared_log = shared_log
        self._results = {}
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
            header, text="🔍  Subdomain Reconnaissance",
            font=FONTS["title"], text_color=COLORS["text_primary"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text=f"Scan {len(DEFAULT_SUBDOMAINS)} subdomain umum secara multithreaded untuk domain target",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        # === Input + Progress ===
        input_card = ModuleCard(self)
        input_card.grid(row=1, column=0, sticky="ew", padx=PADDING_LG, pady=PADDING_MD)
        input_card.grid_columnconfigure(1, weight=1)

        SectionLabel(input_card, "Domain Target:").grid(
            row=0, column=0, padx=PADDING_MD, pady=PADDING_MD, sticky="w"
        )
        self._domain_entry = StyledEntry(input_card, placeholder="Contoh: example.com")
        self._domain_entry.insert(0, "github.com")
        self._domain_entry.grid(row=0, column=1, padx=PADDING_SM, pady=PADDING_MD, sticky="ew")

        self._run_btn = PrimaryButton(input_card, "🔍  Mulai Scan", command=self._start_recon)
        self._run_btn.grid(row=0, column=2, padx=(PADDING_SM, PADDING_MD), pady=PADDING_MD)

        # Progress bar
        self._progress = ProgressSection(input_card, label="Progres Scan")
        self._progress.grid(row=1, column=0, columnspan=3,
                            padx=PADDING_MD, pady=(0, PADDING_MD), sticky="ew")

        # === Scrollable Result List ===
        result_card = ModuleCard(self, title="Subdomain yang Ditemukan")
        result_card.grid(row=2, column=0, sticky="nsew", padx=PADDING_LG, pady=PADDING_SM)

        # Scrollable frame untuk daftar hasil
        self._scroll_frame = ctk.CTkScrollableFrame(
            result_card,
            fg_color=COLORS["bg_dark"],
            corner_radius=8,
            scrollbar_button_color=COLORS["accent_blue"],
            scrollbar_button_hover_color=COLORS["accent_purple"],
        )
        self._scroll_frame.pack(fill="both", expand=True, padx=PADDING_MD, pady=(0, PADDING_MD))

        # Placeholder saat belum ada data
        self._empty_label = ctk.CTkLabel(
            self._scroll_frame,
            text="Jalankan scan untuk melihat hasil...",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        )
        self._empty_label.pack(pady=30)

        # === Statistik ringkas ===
        stats_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_SM))

        self._stat_found = ctk.CTkLabel(
            stats_frame, text="Ditemukan: —",
            font=FONTS["label"], text_color=COLORS["accent_green"]
        )
        self._stat_found.pack(side="left", padx=(0, PADDING_MD))

        self._stat_total = ctk.CTkLabel(
            stats_frame, text="Dicek: —",
            font=FONTS["label"], text_color=COLORS["text_secondary"]
        )
        self._stat_total.pack(side="left")

        # === Log ===
        log_card = ModuleCard(self, title="Log Proses")
        log_card.grid(row=3, column=0, sticky="ew", padx=PADDING_LG, pady=(PADDING_SM, PADDING_LG))
        self._log = LogArea(log_card, height=110)
        self._log.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_MD))

    # ---------------------------------------------------------------
    # Logika Scan
    # ---------------------------------------------------------------
    def _start_recon(self):
        domain = self._domain_entry.get().strip()
        if not domain:
            self._log.append("⚠ Masukkan nama domain terlebih dahulu.")
            return

        self._run_btn.configure(state="disabled", text="⏳ Scanning...")
        self._log.clear()
        self._progress.reset()
        self._clear_results()

        threading.Thread(
            target=self._run_in_background,
            args=(domain,),
            daemon=True
        ).start()

    def _clear_results(self):
        """Hapus semua widget hasil sebelumnya dari scroll frame."""
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        self._empty_label = ctk.CTkLabel(
            self._scroll_frame,
            text="Scanning...",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        )
        self._empty_label.pack(pady=30)

    def _run_in_background(self, domain: str):
        def log_cb(msg):
            self.after(0, self._log.append, msg)
            if self._shared_log:
                self.after(0, self._shared_log.append, msg)

        def progress_cb(current, total):
            self.after(0, self._progress.set_progress, current, total)

        try:
            result = run_subdomain_recon(
                domain=domain,
                log_callback=log_cb,
                progress_callback=progress_cb,
            )
            self._results = result
            self.after(0, self._show_results, result)
        except Exception as exc:
            self.after(0, self._log.append, f"❌ Error: {exc}")
        finally:
            self.after(0, self._run_btn.configure, {
                "state": "normal", "text": "🔍  Mulai Scan"
            })

    def _show_results(self, result: dict):
        """Menampilkan daftar subdomain yang ditemukan di scrollable frame."""
        # Bersihkan placeholder
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()

        found = result.get("found", [])
        total = result.get("total", 0)

        self._stat_found.configure(text=f"Ditemukan: {len(found)}")
        self._stat_total.configure(text=f"Dicek: {total}")

        if not found:
            ctk.CTkLabel(
                self._scroll_frame,
                text="Tidak ada subdomain aktif yang ditemukan.",
                font=FONTS["body"], text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        # Header tabel
        header = ctk.CTkFrame(self._scroll_frame, fg_color=COLORS["bg_light"], corner_radius=6)
        header.pack(fill="x", pady=(0, 4), padx=4)
        header.grid_columnconfigure((0, 1, 2), weight=1)

        for col, h_text in enumerate(["FQDN", "IP Address(es)", "Status"]):
            ctk.CTkLabel(
                header, text=h_text, font=FONTS["label"],
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=col, padx=10, pady=6, sticky="w")

        # Baris hasil
        for i, item in enumerate(found):
            row_color = COLORS["bg_medium"] if i % 2 == 0 else COLORS["bg_dark"]
            row = ctk.CTkFrame(self._scroll_frame, fg_color=row_color, corner_radius=4)
            row.pack(fill="x", pady=1, padx=4)
            row.grid_columnconfigure((0, 1, 2), weight=1)

            # FQDN
            ctk.CTkLabel(
                row, text=item["fqdn"],
                font=FONTS["mono_sm"], text_color=COLORS["accent_cyan"]
            ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # IP
            addr_text = "\n".join(item["addresses"]) if item["addresses"] else "—"
            ctk.CTkLabel(
                row, text=addr_text,
                font=FONTS["mono_sm"], text_color=COLORS["text_primary"]
            ).grid(row=0, column=1, padx=10, pady=5, sticky="w")

            # Status badge (selalu FOUND di sini karena kita hanya tampilkan yang found)
            badge_frame = ctk.CTkFrame(row, fg_color="transparent")
            badge_frame.grid(row=0, column=2, padx=10, pady=5, sticky="w")

            ctk.CTkLabel(
                badge_frame, text="● FOUND",
                font=FONTS["label"], text_color=COLORS["accent_green"]
            ).pack(side="left")

    def get_results(self) -> dict:
        return self._results
