"""DuckDuckGo HTML search backend."""

import re
from urllib.parse import quote_plus

import requests

from core.session import PrivacySession
from processing.parser import normalize_result


class DuckDuckGoEngine:
    name = "duckduckgo"

    def __init__(self, session: PrivacySession):
        self.session = session

    @staticmethod
    def _is_ad_or_tracking_link(url: str) -> bool:
        probe = (url or "").lower()
        return any(
            marker in probe
            for marker in (
                "/y.js?",
                "ad_domain",
                "bing ads redirect",
                "bing.com/aclick",
            )
        )

    def _fetch_html(self, endpoint: str) -> str:
        """Fetch page with bounded timeout and retry for unstable Tor circuits."""
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
        encoded = quote_plus(query.strip())
        endpoint = f"https://html.duckduckgo.com/html/?q={encoded}"
        html_text = self._fetch_html(endpoint)
        title_link_pattern = re.compile(
            r'<a[^>]*class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>',
            flags=re.IGNORECASE | re.DOTALL,
        )
        snippet_pattern = re.compile(
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>|<div[^>]*class="result__snippet"[^>]*>(.*?)</div>',
            flags=re.IGNORECASE | re.DOTALL,
        )

        snippets = []
        for left, right in snippet_pattern.findall(html_text):
            snippets.append(left or right)

        rows: list[dict[str, str]] = []
        for idx, match in enumerate(title_link_pattern.finditer(html_text)):
            raw_url = match.group("url")
            if self._is_ad_or_tracking_link(raw_url):
                continue

            record = normalize_result(
                title=match.group("title"),
                url=raw_url,
                summary=snippets[idx] if idx < len(snippets) else "",
                source=self.name,
            )
            if not record["url"]:
                continue
            rows.append(record)
            if len(rows) >= limit:
                break

        return rows
