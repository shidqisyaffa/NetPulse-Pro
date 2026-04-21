"""
core/doh_traveler.py
====================
Modul DNS Traveler (DoH - DNS over HTTPS).
Mengecek konsistensi resolusi IP suatu domain menggunakan
API DoH dari Google dan Cloudflare secara bersamaan.
Berguna untuk mendeteksi DNS poisoning atau geo-blocking.
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


# -----------------------------------------------------------------------
# Endpoint DoH (DNS over HTTPS)
# -----------------------------------------------------------------------
DOH_PROVIDERS = {
    "Google DoH":     "https://dns.google/resolve",
    "Cloudflare DoH": "https://cloudflare-dns.com/dns-query",
}

# Timeout untuk HTTP request ke endpoint DoH
REQUEST_TIMEOUT = 6  # detik


def _query_doh(provider_name: str, endpoint: str, domain: str) -> dict:
    """
    Melakukan satu DoH query ke provider tertentu.

    Args:
        provider_name : Nama provider (e.g. "Google DoH")
        endpoint      : URL endpoint DoH
        domain        : Domain yang akan di-resolve

    Returns:
        dict dengan keys: provider, domain, addresses, status, raw_response
    """
    headers = {
        "Accept": "application/dns-json",  # Format JSON standar RFC 8484
    }
    params = {
        "name": domain,
        "type": "A",  # Hanya query IPv4
    }

    try:
        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        # Ekstrak semua record A dari respons
        addresses = []
        if "Answer" in data:
            for record in data["Answer"]:
                if record.get("type") == 1:  # type 1 = A record (IPv4)
                    addresses.append(record.get("data", ""))

        return {
            "provider":     provider_name,
            "domain":       domain,
            "addresses":    addresses,
            "status":       "OK" if addresses else "NO_RECORD",
            "raw_response": data,
        }

    except requests.exceptions.Timeout:
        return {
            "provider":     provider_name,
            "domain":       domain,
            "addresses":    [],
            "status":       "TIMEOUT",
            "raw_response": {},
        }
    except Exception as exc:
        return {
            "provider":     provider_name,
            "domain":       domain,
            "addresses":    [],
            "status":       f"ERROR: {str(exc)[:60]}",
            "raw_response": {},
        }


def run_doh_check(domain: str, log_callback=None) -> dict:
    """
    Menjalankan DoH check ke semua provider secara concurrent.

    Args:
        domain       : Domain target yang akan dicek
        log_callback : Fungsi callback(str) untuk logging ke UI

    Returns:
        dict berisi:
          - results   : list hasil dari setiap provider
          - consistent: bool, apakah semua provider mengembalikan IP yang sama
          - summary   : string ringkasan
    """
    def _log(msg: str):
        if log_callback:
            log_callback(msg)

    _log(f"[DNS Traveler] Memulai DoH check untuk domain: {domain}")

    results = []

    # Query semua provider secara paralel
    with ThreadPoolExecutor(max_workers=len(DOH_PROVIDERS)) as executor:
        futures = {
            executor.submit(_query_doh, name, url, domain): name
            for name, url in DOH_PROVIDERS.items()
        }

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result["status"] == "OK":
                addr_str = ", ".join(result["addresses"])
                _log(f"  ✓ {result['provider']}: {addr_str}")
            else:
                _log(f"  ✗ {result['provider']}: {result['status']}")

    # Cek konsistensi: apakah semua provider memberikan IP yang sama?
    all_address_sets = [
        frozenset(r["addresses"]) for r in results if r["status"] == "OK"
    ]

    if len(all_address_sets) < 2:
        consistent = False
        summary = "Tidak cukup data untuk menentukan konsistensi."
    elif all(s == all_address_sets[0] for s in all_address_sets):
        consistent = True
        summary = "✅ Konsisten — Semua provider DoH mengembalikan IP yang sama."
    else:
        consistent = False
        summary = "⚠️  Inkonsisten — Provider DoH mengembalikan IP yang berbeda!"

    _log(f"[DNS Traveler] {summary}")

    return {
        "results":    results,
        "consistent": consistent,
        "summary":    summary,
        "domain":     domain,
    }
