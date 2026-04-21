"""
main.py
=======
Entry point aplikasi NetPulse Pro.
Jalankan file ini untuk memulai aplikasi:

    python main.py

Atau jika menggunakan virtual environment:
    venv\\Scripts\\activate
    python main.py

Pastikan semua dependency sudah terinstall:
    pip install -r requirements.txt
"""

import sys
import os

# ── Tambahkan root folder ke sys.path ─────────────────────────────────
# Ini memastikan semua import (core.*, gui.*) bisa ditemukan
# terlepas dari direktori mana user menjalankan script.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ── Cek ketersediaan library sebelum memulai ─────────────────────────
def _check_dependencies():
    """Memeriksa apakah semua library wajib sudah terinstall."""
    required = {
        "customtkinter": "customtkinter",
        "matplotlib":    "matplotlib",
        "dns":           "dnspython",
        "requests":      "requests",
    }
    missing = []
    for module_name, pip_name in required.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print("=" * 60)
        print("❌ Library berikut belum terinstall:")
        for lib in missing:
            print(f"   • {lib}")
        print("\n💡 Jalankan perintah berikut untuk menginstall:")
        print(f"   pip install {' '.join(missing)}")
        print("   atau:")
        print("   pip install -r requirements.txt")
        print("=" * 60)
        sys.exit(1)


def main():
    """Fungsi utama: inisialisasi dan jalankan aplikasi."""
    _check_dependencies()

    # Import setelah dependency check berhasil
    from gui.app import NetPulseApp

    app = NetPulseApp()

    # Jalankan event loop utama tkinter
    app.mainloop()


if __name__ == "__main__":
    main()
