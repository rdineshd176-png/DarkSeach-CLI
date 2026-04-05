"""Onion source search backend (Tor mode only)."""

import re
from urllib.parse import quote_plus, urlparse

from core.session import PrivacySession
from processing.parser import normalize_result


class OnionEngine:
    """Fetch onion-focused sources using a Tor-routed index page."""

    name = "onion"

    def __init__(self, session: PrivacySession):
        self.session = session

    def search(self, query: str, limit: int = 7) -> list[dict[str, str]]:
        # Ahmia indexes onion services and is accessible through Tor routing.
        endpoint = f"https://ahmia.fi/search/?q={quote_plus(query.strip())}"
        response = self.session.get(endpoint)
        response.raise_for_status()

        html_text = response.text
        pattern = re.compile(
            r'<a[^>]*href="(?P<url>https?://[^"]+)"[^>]*>(?P<title>.*?)</a>',
            flags=re.IGNORECASE | re.DOTALL,
        )

        rows: list[dict[str, str]] = []
        for match in pattern.finditer(html_text):
            url = match.group("url").strip()
            host = (urlparse(url).hostname or "").lower()
            if ".onion" not in host:
                continue

            record = normalize_result(
                title=match.group("title"),
                url=url,
                summary="Onion source indexed for privacy-focused research.",
                source=self.name,
            )
            rows.append(record)
            if len(rows) >= limit:
                break

        return rows
