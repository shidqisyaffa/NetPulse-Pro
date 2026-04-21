"""
core/health_check.py
====================
Modul Smart Health Check.
Melakukan ping ke IP yang ditemukan dan menampilkan status
Online (hijau) atau Offline (merah) secara visual di UI.

Catatan Platform:
  - Windows: Menggunakan 'ping -n 1 -w 1000 <ip>'
  - Linux/Mac: Menggunakan 'ping -c 1 -W 1 <ip>'
  Tidak memerlukan admin privileges untuk ICMP ping dasar di Windows.
"""

import subprocess
import platform
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# -----------------------------------------------------------------------
# Konfigurasi Ping
# -----------------------------------------------------------------------
PING_TIMEOUT_MS = 2000  # Timeout dalam milidetik (untuk Windows -w flag)
PING_TIMEOUT_S  = 2     # Timeout dalam detik   (untuk Linux -W flag)
MAX_WORKERS     = 15    # Thread worker untuk ping paralel


def _build_ping_command(ip: str) -> list[str]:
    """
    Membangun command ping yang sesuai dengan OS yang digunakan.

    Args:
        ip : Alamat IP yang akan di-ping

    Returns:
        List string yang siap dijalankan sebagai subprocess
    """
    os_name = platform.system().lower()

    if os_name == "windows":
        # -n 1 : kirim 1 paket
        # -w   : timeout dalam milidetik
        return ["ping", "-n", "1", "-w", str(PING_TIMEOUT_MS), ip]
    else:
        # -c 1 : kirim 1 paket
        # -W   : timeout dalam detik
        return ["ping", "-c", "1", "-W", str(PING_TIMEOUT_S), ip]


def _ping_single_ip(ip: str) -> dict:
    """
    Melakukan ping ke satu IP dan mengukur round-trip time.

    Args:
        ip : Alamat IP target

    Returns:
        dict dengan keys: ip, online, rtt_ms, message
    """
    cmd = _build_ping_command(ip)

    try:
        start_time = time.perf_counter()
        result = subprocess.run(
            cmd,
            capture_output=True,   # Tangkap stdout & stderr
            text=True,
            timeout=PING_TIMEOUT_S + 2,
            creationflags=(
                subprocess.CREATE_NO_WINDOW  # Sembunyikan window CMD di Windows
                if platform.system().lower() == "windows"
                else 0
            ),
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Return code 0 = berhasil, selain itu = gagal / timeout
        online = result.returncode == 0

        if online:
            # Coba ekstrak RTT dari output ping
            rtt_ms = round(elapsed_ms, 1)
            message = f"Online — RTT ≈ {rtt_ms} ms"
        else:
            rtt_ms = None
            message = "Offline / Unreachable"

        return {
            "ip":      ip,
            "online":  online,
            "rtt_ms":  rtt_ms,
            "message": message,
        }

    except subprocess.TimeoutExpired:
        return {
            "ip":      ip,
            "online":  False,
            "rtt_ms":  None,
            "message": "Timeout",
        }
    except FileNotFoundError:
        # Ping binary tidak ditemukan
        return {
            "ip":      ip,
            "online":  False,
            "rtt_ms":  None,
            "message": "ERROR: ping binary tidak ditemukan",
        }
    except Exception as exc:
        return {
            "ip":      ip,
            "online":  False,
            "rtt_ms":  None,
            "message": f"ERROR: {str(exc)[:60]}",
        }


def run_health_check(
    ip_list: list[str],
    log_callback=None,
    progress_callback=None,
) -> list[dict]:
    """
    Menjalankan health check (ping) ke semua IP secara concurrent.

    Args:
        ip_list           : List alamat IP yang akan dicek
        log_callback      : Fungsi callback(str) untuk logging ke UI
        progress_callback : Fungsi callback(current, total) untuk progress bar

    Returns:
        List of result dicts, diurutkan: Online dulu, lalu Offline.
    """
    def _log(msg: str):
        if log_callback:
            log_callback(msg)

    if not ip_list:
        _log("[Health Check] Tidak ada IP yang perlu dicek.")
        return []

    # Deduplikasi IP list
    unique_ips = list(dict.fromkeys(ip_list))
    total = len(unique_ips)

    _log(f"[Health Check] Memulai ping ke {total} alamat IP unik")
    _log(f"[Health Check] Platform: {platform.system()} | Workers: {MAX_WORKERS}")

    results = []
    completed = 0

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, total)) as executor:
        future_map = {
            executor.submit(_ping_single_ip, ip): ip
            for ip in unique_ips
        }

        for future in as_completed(future_map):
            result = future.result()
            results.append(result)
            completed += 1

            # Update progress bar di UI
            if progress_callback:
                progress_callback(completed, total)

            # Log dengan indikator warna teks
            status_icon = "🟢" if result["online"] else "🔴"
            _log(
                f"  {status_icon} {result['ip']:20s} — {result['message']}"
            )

    # Urutkan: Online dulu, lalu Offline
    results.sort(key=lambda r: (not r["online"], r["ip"]))

    online_count = sum(1 for r in results if r["online"])
    _log(
        f"[Health Check] Selesai. "
        f"{online_count}/{total} host Online, "
        f"{total - online_count} Offline."
    )

    return results
