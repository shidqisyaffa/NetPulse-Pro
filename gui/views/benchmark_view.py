"""
gui/views/benchmark_view.py
============================
Panel tampilan untuk modul DNS Speed Benchmark.
Menampilkan form input domain, tombol run, bar chart latensi,
dan area log hasil benchmark.
"""

import threading
import customtkinter as ctk
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (aman untuk embedding)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gui.theme import COLORS, FONTS, PADDING_MD, PADDING_SM, PADDING_LG
from gui.widgets import (
    ModuleCard, PrimaryButton, SecondaryButton,
    StyledEntry, LogArea, SectionLabel, StatusBadge
)
from core.dns_benchmark import run_benchmark


class BenchmarkView(ctk.CTkFrame):
    """
    View untuk modul DNS Speed Benchmark.
    Struktur: Input bar → Chart area → Log area
    """

    def __init__(self, parent, shared_log=None):
        super().__init__(parent, fg_color="transparent")
        self._shared_log = shared_log   # Referensi ke log area global
        self._results = []              # Simpan hasil terakhir
        self._build_ui()

    # ---------------------------------------------------------------
    # Pembangunan UI
    # ---------------------------------------------------------------
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === Header ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING_LG, pady=(PADDING_LG, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="📊  DNS Speed Benchmark",
            font=FONTS["title"], text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Ukur latensi server DNS Google, Cloudflare, OpenDNS, dan lainnya secara bersamaan",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        # === Input + Tombol ===
        input_frame = ModuleCard(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=PADDING_LG, pady=PADDING_MD)
        input_frame.grid_columnconfigure(1, weight=1)

        SectionLabel(input_frame, "Domain Target:").grid(
            row=0, column=0, padx=PADDING_MD, pady=PADDING_SM, sticky="w"
        )
        self._domain_entry = StyledEntry(input_frame, placeholder="Contoh: google.com")
        self._domain_entry.insert(0, "google.com")
        self._domain_entry.grid(row=0, column=1, padx=PADDING_SM, pady=PADDING_MD, sticky="ew")

        self._run_btn = PrimaryButton(input_frame, "▶  Jalankan Benchmark", command=self._start_benchmark)
        self._run_btn.grid(row=0, column=2, padx=(PADDING_SM, PADDING_MD), pady=PADDING_MD)

        # === Chart Area ===
        chart_card = ModuleCard(self, title="Hasil Benchmark — Latensi DNS (ms)")
        chart_card.grid(row=2, column=0, sticky="nsew", padx=PADDING_LG, pady=PADDING_SM)
        self.grid_rowconfigure(2, weight=2)

        self._chart_frame = ctk.CTkFrame(chart_card, fg_color="transparent")
        self._chart_frame.pack(fill="both", expand=True, padx=PADDING_MD, pady=PADDING_SM)

        # Buat figure matplotlib awal (placeholder)
        self._fig, self._ax = plt.subplots(figsize=(8, 3.2), dpi=90)
        self._fig.patch.set_facecolor(COLORS["bg_medium"])
        self._ax.set_facecolor(COLORS["bg_dark"])
        self._ax.set_title("Jalankan benchmark untuk melihat hasil", color=COLORS["text_secondary"])
        self._ax.tick_params(colors=COLORS["text_secondary"])
        for spine in self._ax.spines.values():
            spine.set_color(COLORS["border"])

        # PENTING: Jangan gunakan nama self._canvas — itu dipakai internal CTkFrame!
        # Kita pakai self._mpl_canvas agar tidak terjadi konflik nama atribut.
        self._mpl_canvas = FigureCanvasTkAgg(self._fig, master=self._chart_frame)
        self._mpl_canvas.get_tk_widget().pack(fill="both", expand=True)
        self._mpl_canvas.draw()

        # === Log Area ===
        log_card = ModuleCard(self, title="Log Proses")
        log_card.grid(row=3, column=0, sticky="ew", padx=PADDING_LG, pady=(PADDING_SM, PADDING_LG))

        self._log = LogArea(log_card, height=130)
        self._log.pack(fill="x", padx=PADDING_MD, pady=(0, PADDING_MD))

    # ---------------------------------------------------------------
    # Logika Benchmark
    # ---------------------------------------------------------------
    def _start_benchmark(self):
        """Dipanggil saat tombol Run diklik. Menjalankan benchmark di background thread."""
        domain = self._domain_entry.get().strip()
        if not domain:
            self._log.append("⚠ Masukkan nama domain terlebih dahulu.")
            return

        # Nonaktifkan tombol agar tidak ditekan dua kali
        self._run_btn.configure(state="disabled", text="⏳ Sedang berjalan...")
        self._log.clear()
        self._log.append(f"Memulai benchmark untuk domain: {domain} ...")

        # Jalankan di thread terpisah agar UI tidak freeze
        thread = threading.Thread(
            target=self._run_in_background,
            args=(domain,),
            daemon=True,
        )
        thread.start()

    def _run_in_background(self, domain: str):
        """
        Fungsi yang berjalan di background thread.
        Memanggil core module, lalu meng-update UI via after().
        """
        def log_cb(msg):
            # Thread-safe: update UI via after() dari main thread
            self.after(0, self._log.append, msg)
            if self._shared_log:
                self.after(0, self._shared_log.append, msg)

        try:
            results = run_benchmark(domain=domain, log_callback=log_cb)
            self._results = results
            # Update chart di main thread
            self.after(0, self._update_chart, results)
        except Exception as exc:
            self.after(0, self._log.append, f"❌ Error: {exc}")
        finally:
            # Aktifkan kembali tombol
            self.after(0, self._run_btn.configure, {
                "state": "normal", "text": "▶  Jalankan Benchmark"
            })

    def _update_chart(self, results: list):
        """
        Memperbarui bar chart matplotlib dengan hasil benchmark terbaru.
        Dipanggil di main thread via after().
        """
        self._ax.clear()
        self._fig.patch.set_facecolor(COLORS["bg_medium"])
        self._ax.set_facecolor(COLORS["bg_dark"])

        if not results:
            self._ax.set_title("Tidak ada data", color=COLORS["text_secondary"])
            self._mpl_canvas.draw()
            return

        names    = [r["name"].split(" ")[0] + "\n" + r["ip"] for r in results]
        latencies = [r["latency_ms"] if r["latency_ms"] else 0 for r in results]
        statuses  = [r["status"] for r in results]

        # Warna bar: hijau untuk tercepat, merah untuk timeout
        bar_colors = []
        for i, (lat, st) in enumerate(zip(latencies, statuses)):
            if st == "TIMEOUT":
                bar_colors.append(COLORS["accent_red"])
            elif i == 0:
                bar_colors.append(COLORS["accent_green"])  # Tercepat = hijau
            else:
                bar_colors.append(COLORS["accent_blue"])

        bars = self._ax.bar(
            names, latencies,
            color=bar_colors,
            width=0.55,
            edgecolor=COLORS["border"],
            linewidth=0.8,
        )

        # Anotasi nilai di atas bar
        for bar, lat, st in zip(bars, latencies, statuses):
            label = f"{lat:.1f} ms" if st != "TIMEOUT" else "TIMEOUT"
            self._ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(latencies) * 0.02,
                label,
                ha="center", va="bottom",
                color=COLORS["text_primary"],
                fontsize=8, fontweight="bold"
            )

        self._ax.set_title(
            "Latensi DNS Server (rata-rata 3 query)",
            color=COLORS["text_primary"], pad=10, fontsize=10
        )
        self._ax.set_ylabel("Latensi (ms)", color=COLORS["text_secondary"], fontsize=9)
        self._ax.tick_params(axis="x", colors=COLORS["text_secondary"], labelsize=7.5)
        self._ax.tick_params(axis="y", colors=COLORS["text_secondary"], labelsize=8)

        for spine in self._ax.spines.values():
            spine.set_color(COLORS["border"])

        self._ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}"))
        self._fig.tight_layout(pad=1.2)
        self._mpl_canvas.draw()

    def get_results(self) -> list:
        """Mengembalikan hasil benchmark terakhir (untuk export)."""
        return self._results
