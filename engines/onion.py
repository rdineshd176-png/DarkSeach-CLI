"""Onion source search backend (Tor mode only)."""

import re
from urllib.parse import quote_plus, urlparse

import requests

from core.session import PrivacySession
from processing.parser import normalize_result


class OnionEngine:
    """Fetch onion-focused sources using a Tor-routed index page."""

    name = "onion"

    def __init__(self, session: PrivacySession):
        self.session = session

    def _fetch_html(self, endpoint: str) -> str:
        previous_timeout = self.session.config.timeout
        self.session.config.timeout = 10
        try:
            last_error: Exception | None = None
            for _ in range(2):
                try:
                    response = self.session.get(endpoint)
                    response.raise_for_status()
                    return response.text
                except (requests.Timeout, requests.RequestException) as exc:
                    last_error = exc
            raise RuntimeError("[ERROR] Search request failed. Try again.") from last_error
        finally:
            self.session.config.timeout = previous_timeout

    def search(self, query: str, limit: int = 7) -> list[dict[str, str]]:
        # Ahmia indexes onion services and is accessible through Tor routing.
        endpoint = f"https://ahmia.fi/search/?q={quote_plus(query.strip())}"
        html_text = self._fetch_html(endpoint)

        block_pattern = re.compile(
            r'<li[^>]*class="result"[^>]*>(?P<block>.*?)</li>|<article[^>]*class="result"[^>]*>(?P<alt_block>.*?)</article>',
            flags=re.IGNORECASE | re.DOTALL,
        )
        link_pattern = re.compile(
            r'<a[^>]*href="(?P<url>https?://[^"]+)"[^>]*>(?P<title>.*?)</a>',
            flags=re.IGNORECASE | re.DOTALL,
        )
        snippet_pattern = re.compile(
            r'<p[^>]*>(?P<snippet>.*?)</p>|<div[^>]*class="result-content"[^>]*>(?P<alt_snippet>.*?)</div>',
            flags=re.IGNORECASE | re.DOTALL,
        )

        rows: list[dict[str, str]] = []
        for block_match in block_pattern.finditer(html_text):
            block = block_match.group("block") or block_match.group("alt_block") or ""
            link_match = link_pattern.search(block)
            if not link_match:
                continue

            url = link_match.group("url").strip()
            host = (urlparse(url).hostname or "").lower()
            if not host.endswith(".onion"):
                continue

            snippet_match = snippet_pattern.search(block)
            snippet = ""
            if snippet_match:
                snippet = snippet_match.group("snippet") or snippet_match.group("alt_snippet") or ""

            record = normalize_result(
                title=link_match.group("title"),
                url=url,
                summary=snippet or "Onion source discovered through Ahmia index.",
                source=self.name,
            )
            if not record["url"]:
                continue
            rows.append(record)
            if len(rows) >= limit:
                break

        return rows
