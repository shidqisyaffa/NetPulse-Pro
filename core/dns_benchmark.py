"""
core/dns_benchmark.py
=====================
Modul DNS Speed Benchmark.
Melakukan query DNS ke beberapa server secara bersamaan menggunakan
concurrent.futures.ThreadPoolExecutor untuk performa maksimal.
"""

import time
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed


# -----------------------------------------------------------------------
# Daftar DNS Server yang akan di-benchmark
# -----------------------------------------------------------------------
DNS_SERVERS = {
    "Google (8.8.8.8)":       "8.8.8.8",
    "Cloudflare (1.1.1.1)":   "1.1.1.1",
    "OpenDNS (208.67.222.222)": "208.67.222.222",
    "Google Alt (8.8.4.4)":   "8.8.4.4",
    "Quad9 (9.9.9.9)":        "9.9.9.9",
}

# Domain yang digunakan sebagai target query benchmark
BENCHMARK_DOMAIN = "google.com"

# Jumlah percobaan query per server untuk rata-rata yang lebih akurat
QUERY_ATTEMPTS = 3


def _query_single_server(name: str, server_ip: str, domain: str) -> dict:
    """
    Melakukan DNS query ke satu server dan mengukur latensinya.

    Args:
        name        : Nama tampilan server DNS (e.g. "Google (8.8.8.8)")
        server_ip   : Alamat IP server DNS
        domain      : Domain yang akan di-query

    Returns:
        dict dengan keys: name, ip, latency_ms, status, answers
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server_ip]
    resolver.timeout = 3        # Timeout per query (detik)
    resolver.lifetime = 5       # Lifetime keseluruhan (detik)

    latencies = []
    answers = []

    for attempt in range(QUERY_ATTEMPTS):
        try:
            start = time.perf_counter()  # Timer presisi tinggi
            response = resolver.resolve(domain, "A")
            elapsed = (time.perf_counter() - start) * 1000  # Konversi ke ms
            latencies.append(elapsed)

            # Simpan hasil resolusi hanya dari percobaan pertama
            if attempt == 0:
                answers = [str(r) for r in response]

        except dns.exception.Timeout:
            latencies.append(None)
        except Exception:
            latencies.append(None)

    # Hitung rata-rata latensi (abaikan yang None / gagal)
    valid = [l for l in latencies if l is not None]
    avg_latency = round(sum(valid) / len(valid), 2) if valid else None

    return {
        "name":       name,
        "ip":         server_ip,
        "latency_ms": avg_latency,
        "status":     "OK" if avg_latency is not None else "TIMEOUT",
        "answers":    answers,
    }


def run_benchmark(
    domain: str = BENCHMARK_DOMAIN,
    log_callback=None
) -> list[dict]:
    """
    Menjalankan benchmark DNS secara concurrent ke semua server.

    Args:
        domain       : Domain yang akan di-resolve
        log_callback : Fungsi callback(message: str) untuk logging ke UI

    Returns:
        List of result dicts, diurutkan berdasarkan latency (terkecil duluan)
    """
    results = []

    def _log(msg: str):
        if log_callback:
            log_callback(msg)

    _log(f"[DNS Benchmark] Memulai benchmark ke domain: {domain}")
    _log(f"[DNS Benchmark] Server yang diuji: {', '.join(DNS_SERVERS.keys())}")

    # ThreadPoolExecutor mengeksekusi semua query secara paralel
    with ThreadPoolExecutor(max_workers=len(DNS_SERVERS)) as executor:
        future_to_name = {
            executor.submit(_query_single_server, name, ip, domain): name
            for name, ip in DNS_SERVERS.items()
        }

        for future in as_completed(future_to_name):
            result = future.result()
            results.append(result)

            # Log setiap hasil yang masuk ke UI
            if result["status"] == "OK":
                _log(
                    f"  ✓ {result['name']}: {result['latency_ms']} ms  "
                    f"→ {', '.join(result['answers'])}"
                )
            else:
                _log(f"  ✗ {result['name']}: TIMEOUT / GAGAL")

    # Urutkan: yang berhasil dulu (terkecil), lalu yang gagal
    results.sort(
        key=lambda r: (r["latency_ms"] is None, r["latency_ms"] or float("inf"))
    )

    _log(
        f"[DNS Benchmark] Selesai. "
        f"Server tercepat: {results[0]['name']} ({results[0]['latency_ms']} ms)"
    )
    return results
