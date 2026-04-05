"""Privacy-aware request session manager."""

from pathlib import Path
from typing import Dict, Optional

import requests

from core.config import AppConfig
from core.tor import tor_proxies
from privacy.fingerprint import build_random_headers, load_user_agents, random_delay


class PrivacySession:
    """Request wrapper that handles Tor routing and anti-fingerprinting."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.user_agents = load_user_agents(
            Path(__file__).resolve().parents[1] / "data" / "user_agents.txt"
        )
        self._session = requests.Session()
        self._request_count = 0
        self._rotation_threshold = 4
        self.rotate_session(force=True)

    def rotate_session(self, force: bool = False) -> None:
        """Rotate session identity to reduce fingerprint stability."""
        if not force and self._request_count < self._rotation_threshold:
            return

        self._session.close()
        self._session = requests.Session()
        self._session.headers.clear()
        self._session.headers.update(build_random_headers(self.user_agents))
        self._request_count = 0

    def get(self, url: str, params: Optional[Dict[str, str]] = None) -> requests.Response:
        """Perform Tor-routed GET request with random delay and periodic rotation."""
        random_delay(self.config.anon)
        self.rotate_session()

        response = self._session.get(
            url,
            params=params,
            proxies=tor_proxies(self.config.tor_proxy),
            timeout=self.config.timeout,
        )
        self._request_count += 1
        return response
