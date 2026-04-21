"""
gui/widgets.py
==============
Komponen widget reusable yang digunakan di seluruh aplikasi.
Semua widget mengikuti tema dark mode dari gui/theme.py.
"""

import customtkinter as ctk
from gui.theme import COLORS, FONTS, CORNER_RADIUS, PADDING_MD, PADDING_SM


# ═══════════════════════════════════════════════════════════════════════
# ModuleCard — Container kartu untuk setiap modul
# ═══════════════════════════════════════════════════════════════════════
class ModuleCard(ctk.CTkFrame):
    """Frame berbentuk kartu dengan border dan background medium."""

    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_medium"],
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        if title:
            ctk.CTkLabel(
                self,
                text=title,
                font=FONTS["heading"],
                text_color=COLORS["text_primary"],
            ).pack(anchor="w", padx=PADDING_MD, pady=(PADDING_MD, PADDING_SM))


# ═══════════════════════════════════════════════════════════════════════
# PrimaryButton — Tombol utama bergradien biru
# ═══════════════════════════════════════════════════════════════════════
class PrimaryButton(ctk.CTkButton):
    """Tombol aksi utama dengan warna aksen biru."""

    def __init__(self, parent, text: str, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color=COLORS["accent_blue"],
            hover_color="#3B6FD4",
            text_color="#FFFFFF",
            font=FONTS["label"],
            corner_radius=CORNER_RADIUS,
            height=38,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════
# SecondaryButton — Tombol sekunder bergaris tepi
# ═══════════════════════════════════════════════════════════════════════
class SecondaryButton(ctk.CTkButton):
    """Tombol sekunder dengan border dan background transparan."""

    def __init__(self, parent, text: str, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            hover_color=COLORS["bg_light"],
            border_color=COLORS["accent_blue"],
            border_width=1,
            text_color=COLORS["accent_blue"],
            font=FONTS["label"],
            corner_radius=CORNER_RADIUS,
            height=38,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════
# StyledEntry — Input field bergaya dark
# ═══════════════════════════════════════════════════════════════════════
class StyledEntry(ctk.CTkEntry):
    """Entry field dengan styling dark mode."""

    def __init__(self, parent, placeholder: str = "", **kwargs):
        super().__init__(
            parent,
            placeholder_text=placeholder,
            placeholder_text_color=COLORS["text_muted"],
            fg_color=COLORS["bg_light"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
            corner_radius=CORNER_RADIUS,
            height=38,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════
# LogArea — Area log scrollable (Text widget-based)
# ═══════════════════════════════════════════════════════════════════════
class LogArea(ctk.CTkTextbox):
    """
    Area teks scrollable untuk menampilkan log proses real-time.
    Menggunakan font monospace agar mudah dibaca.
    """

    def __init__(self, parent, height: int = 160, **kwargs):
        super().__init__(
            parent,
            height=height,
            fg_color=COLORS["bg_darkest"],
            text_color=COLORS["accent_cyan"],
            font=FONTS["mono"],
            corner_radius=CORNER_RADIUS,
            border_color=COLORS["border"],
            border_width=1,
            wrap="word",
            **kwargs,
        )
        self.configure(state="disabled")  # Read-only by default

    def append(self, message: str):
        """
        Menambahkan baris pesan ke akhir log area.
        Thread-safe melalui widget.after() dari caller.
        """
        self.configure(state="normal")
        self.insert("end", message + "\n")
        self.see("end")  # Auto-scroll ke baris terbawah
        self.configure(state="disabled")

    def clear(self):
        """Membersihkan seluruh isi log area."""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


# ═══════════════════════════════════════════════════════════════════════
# StatusBadge — Indikator warna status (Online/Offline/OK/Error)
# ═══════════════════════════════════════════════════════════════════════
class StatusBadge(ctk.CTkLabel):
    """Label kecil berbentuk badge untuk menampilkan status."""

    STATUS_COLORS = {
        "online":  (COLORS["accent_green"],  "#FFFFFF"),
        "offline": (COLORS["accent_red"],    "#FFFFFF"),
        "ok":      (COLORS["accent_green"],  "#FFFFFF"),
        "error":   (COLORS["accent_red"],    "#FFFFFF"),
        "warning": (COLORS["accent_yellow"], "#1A1E29"),
        "timeout": (COLORS["accent_orange"], "#FFFFFF"),
        "info":    (COLORS["accent_blue"],   "#FFFFFF"),
    }

    def __init__(self, parent, status: str = "info", text: str = "", **kwargs):
        key = status.lower()
        fg, txt = self.STATUS_COLORS.get(key, (COLORS["bg_light"], COLORS["text_primary"]))
        super().__init__(
            parent,
            text=text or status.upper(),
            font=FONTS["small"],
            fg_color=fg,
            text_color=txt,
            corner_radius=6,
            padx=8,
            pady=2,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════
# SectionLabel — Label judul seksi
# ═══════════════════════════════════════════════════════════════════════
class SectionLabel(ctk.CTkLabel):
    """Label untuk judul sebuah seksi/kelompok konten."""

    def __init__(self, parent, text: str, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=FONTS["subhead"],
            text_color=COLORS["text_secondary"],
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════
# ProgressSection — Wrapper progress bar dengan label
# ═══════════════════════════════════════════════════════════════════════
class ProgressSection(ctk.CTkFrame):
    """Frame yang berisi progress bar dan label persentase."""

    def __init__(self, parent, label: str = "Progress", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.label_text = label
        self._label = ctk.CTkLabel(
            self,
            text=label,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        self._label.pack(anchor="w")

        self._bar = ctk.CTkProgressBar(
            self,
            fg_color=COLORS["bg_light"],
            progress_color=COLORS["accent_blue"],
            corner_radius=4,
            height=8,
        )
        self._bar.pack(fill="x", pady=(2, 0))
        self._bar.set(0)

    def set_progress(self, current: int, total: int):
        """Memperbarui nilai progress bar dan label."""
        ratio = current / total if total > 0 else 0
        self._bar.set(ratio)
        pct = int(ratio * 100)
        self._label.configure(text=f"{self.label_text} — {pct}% ({current}/{total})")

    def reset(self):
        """Reset progress bar ke 0."""
        self._bar.set(0)
        self._label.configure(text=self.label_text)
