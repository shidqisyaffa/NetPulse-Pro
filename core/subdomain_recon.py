"""
core/subdomain_recon.py
=======================
Modul Multithreaded Subdomain Reconnaissance.
Melakukan pencarian subdomain pada domain target menggunakan
concurrent.futures untuk performa optimal di CPU multi-core.
"""

import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed


# -----------------------------------------------------------------------
# Daftar subdomain yang akan dicoba
# -----------------------------------------------------------------------
DEFAULT_SUBDOMAINS = [
    "api", "dev", "mail", "staging", "admin", "blog", "shop",
    "www", "ftp", "smtp", "pop", "imap", "vpn", "cdn",
    "static", "assets", "media", "images", "portal", "app",
    "test", "beta", "docs", "support", "help", "m", "mobile",
]

# Jumlah thread worker (sesuaikan dengan jumlah core CPU)
MAX_WORKERS = 20

# Timeout DNS resolver (detik)
RESOLVE_TIMEOUT = 2


def _resolve_subdomain(subdomain: str, base_domain: str) -> dict:
    """
    Mencoba me-resolve satu subdomain secara DNS.

    Args:
        subdomain   : Prefix subdomain (e.g. "api")
        base_domain : Domain utama (e.g. "example.com")

    Returns:
        dict dengan keys: subdomain, fqdn, found, addresses
    """
    fqdn = f"{subdomain}.{base_domain}"

    resolver = dns.resolver.Resolver()
    resolver.timeout = RESOLVE_TIMEOUT
    resolver.lifetime = RESOLVE_TIMEOUT + 1

    try:
        answers = resolver.resolve(fqdn, "A")
        addresses = [str(r) for r in answers]
        return {
            "subdomain": subdomain,
            "fqdn":      fqdn,
            "found":     True,
            "addresses": addresses,
        }
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
            dns.exception.Timeout, dns.resolver.NoNameservers):
        return {
            "subdomain": subdomain,
            "fqdn":      fqdn,
            "found":     False,
            "addresses": [],
        }
    except Exception:
        return {
            "subdomain": subdomain,
            "fqdn":      fqdn,
            "found":     False,
            "addresses": [],
        }


def run_subdomain_recon(
    domain: str,
    subdomains: list[str] | None = None,
    log_callback=None,
    progress_callback=None,
) -> dict:
    """
    Menjalankan subdomain recon secara multithreaded.

    Args:
        domain            : Domain utama target (e.g. "example.com")
        subdomains        : List subdomain yang akan dicoba (default: DEFAULT_SUBDOMAINS)
        log_callback      : Fungsi callback(str) untuk logging ke UI
        progress_callback : Fungsi callback(current, total) untuk progress bar

    Returns:
        dict berisi:
          - found    : list subdomain yang ditemukan (found=True)
          - not_found: list subdomain yang tidak ditemukan
          - domain   : domain target
          - total    : jumlah total yang dicek
    """
    if subdomains is None:
        subdomains = DEFAULT_SUBDOMAINS

    def _log(msg: str):
        if log_callback:
            log_callback(msg)

    total = len(subdomains)
    _log(f"[Subdomain Recon] Memulai scan {total} subdomain pada: {domain}")
    _log(f"[Subdomain Recon] Menggunakan {MAX_WORKERS} thread worker")

    found = []
    not_found = []
    completed = 0

    # ThreadPoolExecutor: jalankan semua task resolusi secara paralel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {
            executor.submit(_resolve_subdomain, sub, domain): sub
            for sub in subdomains
        }

        for future in as_completed(future_map):
            result = future.result()
            completed += 1

            # Kirim update progress ke UI
            if progress_callback:
                progress_callback(completed, total)

            if result["found"]:
                found.append(result)
                addr_str = ", ".join(result["addresses"])
                _log(f"  🟢 FOUND  {result['fqdn']:40s} → {addr_str}")
            else:
                not_found.append(result)

    found_count = len(found)
    _log(
        f"[Subdomain Recon] Selesai. "
        f"Ditemukan {found_count}/{total} subdomain aktif."
    )

    return {
        "found":     found,
        "not_found": not_found,
        "domain":    domain,
        "total":     total,
    }
