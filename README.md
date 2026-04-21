# ⚡ NetPulse Pro
**Tugas Proyek Mata Kuliah Pemrograman Jaringan**

## 📖 Deskripsi Proyek
**NetPulse Pro** adalah aplikasi diagnostik dan analitik jaringan berbasis *Graphical User Interface* (GUI) yang dibangun menggunakan Python. Proyek ini dikembangkan untuk memfasilitasi pengujian kinerja jaringan, pemantauan koneksi, dan resolusi DNS dalam satu antarmuka yang terintegrasi. 

Aplikasi ini mendemonstrasikan implementasi praktis dari konsep pemrograman jaringan, seperti pengiriman *query* DNS, pelacakan rute (traceroute), hingga penggunaan *Internet Control Message Protocol* (ICMP) untuk pemantauan stabilitas jaringan. Antarmuka aplikasi dirancang dengan `CustomTkinter` untuk memberikan pengalaman pengguna yang modern sekaligus menyederhanakan interaksi dengan alat-alat jaringan berbasis *command-line*.

---

## 📂 Struktur File Proyek
Proyek ini mengadopsi arsitektur *Modular* untuk memisahkan logika pemrosesan jaringan (*backend*) dan antarmuka pengguna (*frontend*). Berikut adalah struktur file dan penjelasannya:

```text
NetPulse Pro/
├── core/                   # Direktori Backend (Logika Jaringan)
│   ├── dns_benchmark.py    # Modul untuk menguji dan membandingkan waktu respons berbagai server DNS.
│   ├── doh_traveler.py     # Modul traceroute tingkat lanjut untuk melacak rute paket dari sumber ke tujuan.
│   ├── health_check.py     # Modul pemantauan koneksi secara real-time (mengukur latensi, jitter, dan packet loss).
│   ├── reporter.py         # Modul untuk mengekspor data dan grafik hasil analisis jaringan menjadi file laporan.
│   └── subdomain_recon.py  # Modul untuk mencari dan memetakan daftar subdomain aktif dari domain target.
│
├── gui/                    # Direktori Frontend (Antarmuka Pengguna)
│   ├── views/              # Direktori berisi halaman-halaman (tab) aplikasi
│   │   ├── benchmark_view.py # Mengatur antarmuka halaman DNS Benchmark.
│   │   ├── dashboard_view.py # Mengatur antarmuka halaman Utama (Dashboard).
│   │   ├── doh_view.py       # Mengatur antarmuka halaman Route Traveler.
│   │   ├── health_view.py    # Mengatur antarmuka halaman Network Health Check.
│   │   └── recon_view.py     # Mengatur antarmuka halaman Subdomain Reconnaissance.
│   ├── app.py              # Logika jendela aplikasi utama, routing menu, dan inisialisasi aplikasi.
│   ├── theme.py            # Konfigurasi skema warna (dark/light) dan gaya visual.
│   └── widgets.py          # Kumpulan komponen antarmuka kustom (tombol, input, grafik) yang dapat dipakai ulang.
│
├── main.py                 # Entry point (titik masuk) utama untuk menjalankan aplikasi.
└── requirements.txt        # Daftar dependency atau library Python yang dibutuhkan oleh proyek ini.
```

---

## ✨ Penjelasan Fitur dan Modul
Aplikasi ini terbagi menjadi 4 fungsi jaringan utama:

1. **DNS Benchmark (`core/dns_benchmark.py`)**
   Fitur ini mengeksekusi *query* ke berbagai server DNS publik secara bersamaan untuk menentukan server dengan waktu resolusi (*resolution time*) tercepat terhadap domain target tertentu.
   
2. **Route Traveler (`core/doh_traveler.py`)**
   Fitur yang mengimplementasikan metode pelacakan rute jaringan (*traceroute*). Modul ini bekerja dengan melacak lompatan (*hops*) perangkat *router* perantara yang dilewati oleh paket data hingga mencapai alamat IP tujuan.

3. **Subdomain Recon (`core/subdomain_recon.py`)**
   Modul ini berfungsi untuk memetakan jejak domain suatu organisasi dengan melakukan pencarian *records* terhadap kemungkinan subdomain yang ada pada domain target. Pemrosesan dilakukan secara *concurrent* untuk mempercepat pencarian massal.

4. **Network Health Check (`core/health_check.py`)**
   Menggunakan paket ICMP (Ping) untuk memantau status kesehatan koneksi terhadap sebuah *host*. Modul ini akan menampilkan metrik *packet loss* dan menyajikan fluktuasi latensi (*jitter*) ke dalam bentuk grafik *real-time*.

---

## 💻 Cuplikan Implementasi Kode
Sebagai representasi pemanfaatan konsep *multithreading* pada aplikasi jaringan, berikut adalah potongan fungsi utama dari modul **DNS Benchmark** (`core/dns_benchmark.py`). Aplikasi mengandalkan `ThreadPoolExecutor` guna menjalankan *query* DNS ke berbagai server publik secara paralel. Hal ini mempercepat keseluruhan proses hingga berkali-kali lipat dan memastikan *UI Thread* tidak terblokir (*freeze*).

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_benchmark(domain: str, log_callback=None) -> list[dict]:
    results = []
    
    # ThreadPoolExecutor mengeksekusi tugas secara paralel
    with ThreadPoolExecutor(max_workers=len(DNS_SERVERS)) as executor:
        
        # Mendaftarkan (submit) fungsi query DNS ke dalam Thread Pool
        future_to_name = {
            executor.submit(_query_single_server, name, ip, domain): name
            for name, ip in DNS_SERVERS.items()
        }

        # Menangkap hasil (result) segera setelah sebuah Thread selesai
        for future in as_completed(future_to_name):
            result = future.result()
            results.append(result)

            # Eksekusi Callback secara aman ke GUI
            if log_callback:
                if result["status"] == "OK":
                    log_callback(f"  ✓ {result['name']}: {result['latency_ms']} ms")
                else:
                    log_callback(f"  ✗ {result['name']}: TIMEOUT / GAGAL")
                
    # Urutkan array akhir berdasarkan latensi terkecil
    results.sort(key=lambda r: (r["latency_ms"] is None, r["latency_ms"] or float("inf")))
    
    return results
```

---

## 🏗️ Arsitektur Sistem & Pemetaan OSI Layer

Alur kerja NetPulse Pro dirancang dan dipetakan langsung dengan pemahaman terhadap lapisan protokol OSI Model, sehingga sangat ideal sebagai bahan studi kasus akademik:

### Pemetaan OSI Layer
| Fitur | Protokol Utama | Lapisan OSI | Penjelasan Teknis |
| :--- | :--- | :--- | :--- |
| **DNS Benchmark** | UDP (Port 53) | Layer 7 (Application) | Mengukur waktu Request-Response paket UDP DNS. |
| **DoH Traveler** | HTTPS / TLS | Layer 7 (Application) | Resolusi nama aman melalui enkripsi SSL/TLS. |
| **Subdomain Recon**| DNS Query | Layer 7 (Application) | Enumerasi rekaman DNS (A, CNAME) secara massal. |
| **Health Check** | ICMP | Layer 3 (Network) | Menggunakan paket Echo Request/Reply untuk mengukur *reachability*. |

### Lapisan Pemrosesan Data
- **Input:** Target berupa alamat IP atau nama domain dimasukkan melalui modul-modul antarmuka di folder `gui/views`.
- **Pemrosesan Asinkron:** Agar GUI tidak mengalami *freeze* (macet) ketika menunggu respons jaringan, aplikasi memanfaatkan **Multithreading** (`concurrent.futures`). Seluruh modul jaringan dari folder `core/` dijalankan di *thread* latar belakang.
- **Output:** Hasil kalkulasi dari *worker thread* diteruskan kembali secara aman ke antarmuka utama untuk di-*render* menjadi teks atau grafik secara langsung (*real-time*) menggunakan *Matplotlib*. Data ini juga dapat diekspor menjadi laporan berkat modul `core/reporter.py`.

---

## 🛠️ Teknologi yang Digunakan
- **Bahasa Pemrograman**: `Python 3.x`
- **Antarmuka Pengguna (GUI)**: `CustomTkinter`
- **Library Jaringan Dasar**: `dnspython` (untuk *query* DNS spesifik).
- **Library Visualisasi Data**: `matplotlib` (untuk menggambar grafik *real-time*).
- **Library Konkurensi**: Modul bawaan `threading` dan `concurrent.futures` untuk *Multithreading*.

---

## 🚀 Panduan Instalasi dan Penggunaan
Langkah-langkah untuk menjalankan aplikasi secara lokal:

1. **Persiapan Virtual Environment:**
   Dianjurkan untuk menggunakan lingkungan virtual (virtual environment) agar dependensi proyek tidak bentrok dengan instalasi Python bawaan sistem.
   ```bash
   python -m venv venv
   ```

2. **Aktivasi Virtual Environment:**
   - **Windows:** `venv\Scripts\activate`
   - **Linux/macOS:** `source venv/bin/activate`

3. **Instalasi Library/Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Menjalankan Aplikasi:**
   Jalankan file utama dari *root* folder:
   ```bash
   python main.py
   ```
   Setelah aplikasi terbuka, pengguna dapat memasukkan nama domain target dan memilih modul analisis yang tersedia pada panel sebelah kiri aplikasi.
