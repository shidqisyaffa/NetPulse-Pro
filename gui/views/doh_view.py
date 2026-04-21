"""
gui/views/doh_view.py
=====================
Panel tampilan untuk modul DNS Traveler (DoH).
Menampilkan input domain, hasil perbandingan IP dari Google & Cloudflare,
dan indikator konsistensi resolusi.
"""

import threading
import customtkinter as ctk

from gui.theme import COLORS, FONTS, PADDING_MD, PADDING_SM, PADDING_LG
from gui.widgets import (
    ModuleCard, PrimaryButton, StyledEntry,
    LogArea, SectionLabel, StatusBadge
)
from core.doh_traveler import run_doh_check


class DohView(ctk.CTkFrame):
    """
    View untuk modul DNS Traveler (DoH - DNS over HTTPS).
    Menampilkan perbandingan IP yang dikembalikan oleh
    Google DoH dan Cloudflare DoH.
    """

    def __init__(self, parent, shared_log=None):
        super().__init__(parent, fg_color="transparent")
        self._shared_log = shared_log
        self._results = {}
        self._result_widgets = {}   # Menyimpan widget hasil agar bisa di-update
        self._build_ui()

    # ---------------------------------------------------------------
    # Pembangunan UI
    # ---------------------------------------------------------------
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # === Header ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING_LG, pady=(PADDING_LG, 0))

        ctk.CTkLabel(
            header, text="🌐  DNS Traveler — DoH Checker",
            font=FONTS["title"], text_color=COLORS["text_primary"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Cek konsistensi resolusi IP menggunakan DNS-over-HTTPS dari Google & Cloudflare",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        # === Input ===
        input_card = ModuleCard(self)
        input_card.grid(row=1, column=0, sticky="ew", padx=PADDING_LG, pady=PADDING_MD)
        input_card.grid_columnconfigure(1, weight=1)

        SectionLabel(input_card, "Domain Target:").grid(
            row=0, column=0, padx=PADDING_MD, pady=PADDING_MD, sticky="w"
        )
        self._domain_entry = StyledEntry(input_card, placeholder="Contoh: facebook.com")
        self._domain_entry.insert(0, "facebook.com")
        self._domain_entry.grid(row=0, column=1, padx=PADDING_SM, pady=PADDING_MD, sticky="ew")

        self._run_btn = PrimaryButton(input_card, "🌐  Cek DoH", command=self._start_check)
        self._run_btn.grid(row=0, column=2, padx=(PADDING_SM, PADDING_MD), pady=PADDING_MD)

        # === Hasil Perbandingan ===
        result_card = ModuleCard(self, title="Hasil Perbandingan IP")
        result_card.grid(row=2, column=0, sticky="ew", padx=PADDING_LG, pady=PADDING_SM)

        self._result_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        self._result_frame.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_MD))
        self._result_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")

        self._build_provider_card(0, "🔵  Google DoH", "google")
        self._build_provider_card(1, "🟠  Cloudflare DoH", "cloudflare")

        # === Indikator Konsistensi ===
        self._consistency_frame = ModuleCard(self)
        self._consistency_frame.grid(row=3, column=0, sticky="ew", padx=PADDING_LG, pady=PADDING_SM)

        self._consistency_label = ctk.CTkLabel(
            self._consistency_frame,
            text="Jalankan pengecekan untuk melihat konsistensi...",
            font=FONTS["subhead"],
            text_color=COLORS["text_muted"],
        )
        self._consistency_label.pack(padx=PADDING_MD, pady=PADDING_MD)

        # === Log ===
        log_card = ModuleCard(self, title="Log Proses")
        log_card.grid(row=4, column=0, sticky="ew", padx=PADDING_LG, pady=(PADDING_SM, PADDING_LG))
        self._log = LogArea(log_card, height=120)
        self._log.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_MD))

    def _build_provider_card(self, col: int, label: str, key: str):
        """Membuat sub-kartu untuk satu provider DoH."""
        frame = ctk.CTkFrame(
            self._result_frame,
            fg_color=COLORS["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        frame.grid(row=0, column=col, padx=PADDING_SM, pady=PADDING_SM, sticky="nsew")

        ctk.CTkLabel(frame, text=label, font=FONTS["subhead"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=12, pady=(10, 4))

        ip_label = ctk.CTkLabel(
            frame, text="—",
            font=FONTS["mono"], text_color=COLORS["accent_cyan"],
            justify="left", wraplength=250
        )
        ip_label.pack(anchor="w", padx=12, pady=(0, 4))

        status_var = ctk.StringVar(value="Menunggu...")
        status_label = ctk.CTkLabel(
            frame, textvariable=status_var,
            font=FONTS["small"], text_color=COLORS["text_secondary"]
        )
        status_label.pack(anchor="w", padx=12, pady=(0, 10))

        # Simpan referensi widget untuk di-update nanti
        self._result_widgets[key] = {
            "ip_label":    ip_label,
            "status_var":  status_var,
        }

    # ---------------------------------------------------------------
    # Logika DoH Check
    # ---------------------------------------------------------------
    def _start_check(self):
        domain = self._domain_entry.get().strip()
        if not domain:
            self._log.append("⚠ Masukkan nama domain terlebih dahulu.")
            return

        self._run_btn.configure(state="disabled", text="⏳ Mengecek...")
        self._log.clear()
        self._consistency_label.configure(
            text="Sedang mengecek konsistensi...",
            text_color=COLORS["text_secondary"]
        )

        # Reset tampilan
        for key, w in self._result_widgets.items():
            w["ip_label"].configure(text="—")
            w["status_var"].set("Mengecek...")

        threading.Thread(
            target=self._run_in_background,
            args=(domain,),
            daemon=True
        ).start()

    def _run_in_background(self, domain: str):
        def log_cb(msg):
            self.after(0, self._log.append, msg)
            if self._shared_log:
                self.after(0, self._shared_log.append, msg)

        try:
            result = run_doh_check(domain=domain, log_callback=log_cb)
            self._results = result
            self.after(0, self._update_ui, result)
        except Exception as exc:
            self.after(0, self._log.append, f"❌ Error: {exc}")
        finally:
            self.after(0, self._run_btn.configure, {
                "state": "normal", "text": "🌐  Cek DoH"
            })

    def _update_ui(self, result: dict):
        """Update tampilan dengan hasil DoH check."""
        provider_key_map = {
            "Google DoH":     "google",
            "Cloudflare DoH": "cloudflare",
        }

        for r in result.get("results", []):
            key = provider_key_map.get(r["provider"])
            if key and key in self._result_widgets:
                w = self._result_widgets[key]
                addrs = r["addresses"]
                if addrs:
                    w["ip_label"].configure(text="\n".join(addrs))
                    w["status_var"].set(f"✓ {len(addrs)} record ditemukan")
                else:
                    w["ip_label"].configure(text="—")
                    w["status_var"].set(f"✗ {r['status']}")

        # Update indikator konsistensi
        summary = result.get("summary", "")
        consistent = result.get("consistent", False)
        color = COLORS["accent_green"] if consistent else COLORS["accent_red"]
        self._consistency_label.configure(text=summary, text_color=color)

    def get_results(self) -> dict:
        return self._results
