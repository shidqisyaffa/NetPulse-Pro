"""
gui/theme.py
============
Definisi tema warna, font, dan konstanta desain untuk NetPulse Pro.
Menggunakan palet warna gelap (dark mode) modern dengan aksen biru-ungu.
"""

# -----------------------------------------------------------------------
# Palet Warna Utama (Dark Mode)
# -----------------------------------------------------------------------
COLORS = {
    # Background layers
    "bg_darkest":   "#0D0F14",   # Latar belakang paling gelap (body)
    "bg_dark":      "#13161E",   # Latar belakang utama
    "bg_medium":    "#1A1E29",   # Card / panel
    "bg_light":     "#222636",   # Elemen hover / input
    "bg_sidebar":   "#0F1219",   # Sidebar

    # Aksen & brand
    "accent_blue":  "#4F8EF7",   # Biru utama
    "accent_purple":"#8B5CF6",   # Ungu
    "accent_cyan":  "#22D3EE",   # Cyan highlight
    "accent_green": "#10B981",   # Hijau (Online / OK)
    "accent_red":   "#EF4444",   # Merah (Offline / Error)
    "accent_yellow":"#F59E0B",   # Kuning (Warning)
    "accent_orange":"#F97316",   # Orange

    # Gradient endpoints
    "grad_start":   "#4F8EF7",
    "grad_end":     "#8B5CF6",

    # Teks
    "text_primary":  "#F0F4FF",   # Teks utama (terang)
    "text_secondary":"#8892AA",   # Teks sekunder (abu-abu)
    "text_muted":    "#4A526A",   # Teks redup

    # Border
    "border":        "#2A3047",
    "border_active": "#4F8EF7",
}

# -----------------------------------------------------------------------
# Konfigurasi Font
# -----------------------------------------------------------------------
FONTS = {
    "title":    ("Segoe UI", 22, "bold"),
    "heading":  ("Segoe UI", 14, "bold"),
    "subhead":  ("Segoe UI", 11, "bold"),
    "body":     ("Segoe UI", 10),
    "small":    ("Segoe UI", 9),
    "mono":     ("Consolas", 10),        # Font monospace untuk log
    "mono_sm":  ("Consolas", 9),
    "label":    ("Segoe UI", 10, "bold"),
}

# -----------------------------------------------------------------------
# Konstanta UI
# -----------------------------------------------------------------------
SIDEBAR_WIDTH  = 220    # Lebar sidebar (pixel)
CORNER_RADIUS  = 10     # Radius sudut elemen
PADDING_LG     = 20     # Padding besar
PADDING_MD     = 12     # Padding medium
PADDING_SM     = 6      # Padding kecil
LOG_HEIGHT     = 160    # Tinggi area log (pixel)

# -----------------------------------------------------------------------
# Ikon teks (unicode) untuk navigasi sidebar
# -----------------------------------------------------------------------
NAV_ICONS = {
    "Dashboard":       "⚡",
    "DNS Benchmark":   "📊",
    "DNS Traveler":    "🌐",
    "Subdomain Recon": "🔍",
    "Health Check":    "💓",
}
