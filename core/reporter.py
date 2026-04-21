"""
core/reporter.py
================
Modul Export & Reporting.
Mengumpulkan semua hasil diagnosa dan menyimpannya ke file JSON
menggunakan pathlib untuk cross-platform path handling.
"""

import json
import platform
from pathlib import Path
from datetime import datetime


def export_report(
    benchmark_results: list | None = None,
    doh_results: dict | None = None,
    recon_results: dict | None = None,
    health_results: list | None = None,
    output_path: str | Path | None = None,
    log_callback=None,
) -> Path:
    """
    Mengeksport semua hasil diagnosa ke file JSON.

    Args:
        benchmark_results : Hasil dari dns_benchmark.run_benchmark()
        doh_results       : Hasil dari doh_traveler.run_doh_check()
        recon_results     : Hasil dari subdomain_recon.run_subdomain_recon()
        health_results    : Hasil dari health_check.run_health_check()
        output_path       : Path output (default: ./diagnostic_report.json)
        log_callback      : Fungsi callback(str) untuk logging ke UI

    Returns:
        Path objek ke file yang telah disimpan
    """
    def _log(msg: str):
        if log_callback:
            log_callback(msg)

    # ---------------------------------------------------------------
    # Susun struktur laporan
    # ---------------------------------------------------------------
    report = {
        "metadata": {
            "app_name":       "NetPulse Pro",
            "version":        "1.0.0",
            "generated_at":   datetime.now().isoformat(),
            "platform":       platform.system(),
            "platform_detail": platform.version(),
        },
        "dns_benchmark": benchmark_results or [],
        "doh_traveler":  doh_results or {},
        "subdomain_recon": recon_results or {},
        "health_check":  health_results or [],
    }

    # ---------------------------------------------------------------
    # Tentukan path output menggunakan pathlib (cross-platform)
    # ---------------------------------------------------------------
    if output_path is None:
        # Default: simpan di direktori kerja saat ini
        output_path = Path.cwd() / "diagnostic_report.json"
    else:
        output_path = Path(output_path)

    # Buat direktori jika belum ada
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------
    # Tulis JSON ke file dengan encoding UTF-8
    # ---------------------------------------------------------------
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False, default=str)

    _log(f"[Reporter] Laporan berhasil disimpan ke: {output_path.resolve()}")
    return output_path
