"""Tor connectivity helpers for DocSearch CLI."""

from typing import Dict

import requests

TOR_PROXY_URL = "socks5h://127.0.0.1:9050"


def tor_proxies() -> Dict[str, str]:
    """Return proxy mapping that prevents DNS leaks via socks5h."""
    return {
        "http": TOR_PROXY_URL,
        "https": TOR_PROXY_URL,
    }


def is_tor_running(timeout: int = 10) -> bool:
    """Validate that Tor SOCKS proxy is reachable and can make outbound requests."""
    test_url = "https://check.torproject.org/api/ip"
    try:
        response = requests.get(
            test_url,
            proxies=tor_proxies(),
            timeout=timeout,
        )
        if response.status_code != 200:
            return False

        payload = response.json()
        return bool(payload.get("IP"))
    except (requests.RequestException, ValueError):
        return False
