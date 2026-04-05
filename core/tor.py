"""Tor connectivity and proxy helpers."""

from typing import Dict

import requests


def tor_proxies(proxy_url: str = "socks5h://127.0.0.1:9050") -> Dict[str, str]:
    """Return SOCKS proxy mapping with remote DNS resolution."""
    return {"http": proxy_url, "https": proxy_url}


def is_tor_running(proxy_url: str = "socks5h://127.0.0.1:9050", timeout: int = 10) -> bool:
    """Check whether Tor SOCKS endpoint is functional for outbound traffic."""
    try:
        response = requests.get(
            "https://check.torproject.org/api/ip",
            proxies=tor_proxies(proxy_url),
            timeout=timeout,
        )
        if response.status_code != 200:
            return False
        payload = response.json()
        return bool(payload.get("IP"))
    except (requests.RequestException, ValueError):
        return False
