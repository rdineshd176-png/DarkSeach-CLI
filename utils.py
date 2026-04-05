"""Utility helpers for DocSearch CLI.

No query history, logs, or telemetry are stored.
"""

import random
import time
from typing import Dict, Optional

# A compact pool of common desktop and mobile user agents.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]


def random_user_agent() -> str:
    """Return a random user agent string for anti-fingerprinting hygiene."""
    return random.choice(USER_AGENTS)


def build_headers() -> Dict[str, str]:
    """Create per-request randomized headers."""
    return {
        "User-Agent": random_user_agent(),
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.7",
        "Connection": "close",
        "DNT": "1",
    }


def apply_request_delay(extra_anon: bool = True) -> None:
    """Sleep before outbound requests to reduce request correlation.

    Base delay is always applied to satisfy privacy requirements.
    Optional anonymous mode adds a small extra jitter.
    """
    base_delay = random.uniform(1.0, 3.0)
    if extra_anon:
        base_delay += random.uniform(0.2, 1.0)
    time.sleep(base_delay)


def truncate_text(text: Optional[str], max_len: int = 220) -> str:
    """Trim and normalize text for cleaner CLI output."""
    if not text:
        return "No summary available."

    cleaned = " ".join(text.split())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."


def colorize(text: str, color: str = "cyan", enabled: bool = True) -> str:
    """Colorize text with ANSI codes (safe no-op when disabled)."""
    if not enabled:
        return text

    palette = {
        "reset": "\033[0m",
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "bold": "\033[1m",
    }
    prefix = palette.get(color, "")
    suffix = palette["reset"] if prefix else ""
    return f"{prefix}{text}{suffix}"
