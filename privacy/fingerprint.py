"""Anti-fingerprinting utilities: rotating UA, headers, and delays."""

import random
import time
from pathlib import Path
from typing import Dict, List

DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]

ACCEPT_HEADERS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "application/json,text/plain,*/*",
    "text/html,application/json;q=0.9,*/*;q=0.8",
]

REFERERS = [
    "https://duckduckgo.com/",
    "https://startpage.com/",
    "https://search.brave.com/",
    "https://www.qwant.com/",
]


def load_user_agents(path: Path) -> List[str]:
    """Load user-agents from file with safe fallback."""
    try:
        rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        agents = [line for line in rows if line and not line.startswith("#")]
        return agents or DEFAULT_USER_AGENTS
    except OSError:
        return DEFAULT_USER_AGENTS


def build_random_headers(user_agents: List[str]) -> Dict[str, str]:
    """Generate per-request randomized browser-like headers."""
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": random.choice(ACCEPT_HEADERS),
        "Accept-Language": random.choice(["en-US,en;q=0.7", "en-GB,en;q=0.8"]),
        "Referer": random.choice(REFERERS),
        "DNT": "1",
        "Connection": "close",
    }


def random_delay(anon_mode: bool) -> None:
    """Apply random delay before requests to reduce correlation."""
    if anon_mode:
        time.sleep(random.uniform(1.0, 5.0))
    else:
        time.sleep(random.uniform(0.1, 0.7))
