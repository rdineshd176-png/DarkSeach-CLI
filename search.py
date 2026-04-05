"""Search engine integration for DocSearch CLI."""

from html import unescape
import re
from typing import Dict, List
from urllib.parse import quote_plus

import requests

from tor import tor_proxies
from utils import apply_request_delay, build_headers, truncate_text


class SearchClient:
    """Privacy-first search client routed through Tor."""

    def __init__(self, engine: str = "duckduckgo", anon_mode: bool = True, timeout: int = 18):
        self.engine = engine
        self.anon_mode = anon_mode
        self.timeout = timeout

    def set_engine(self, engine: str) -> bool:
        normalized = engine.strip().lower()
        if normalized in {"duckduckgo", "searxng"}:
            self.engine = normalized
            return True
        return False

    def set_anon_mode(self, enabled: bool) -> None:
        self.anon_mode = enabled

    def search(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """Run a search with selected engine and return normalized result rows."""
        query = query.strip()
        if not query:
            raise ValueError("Please enter a non-empty search query.")

        limit = max(1, min(limit, 10))
        apply_request_delay(extra_anon=self.anon_mode)

        if self.engine == "searxng":
            return self._search_searxng(query, limit)
        return self._search_duckduckgo(query, limit)

    def _request(self, url: str, params: Dict[str, str] | None = None) -> requests.Response:
        return requests.get(
            url,
            params=params,
            headers=build_headers(),
            proxies=tor_proxies(),
            timeout=self.timeout,
        )

    def _search_searxng(self, query: str, limit: int) -> List[Dict[str, str]]:
        """Use a public SearXNG endpoint with JSON format."""
        endpoint = "https://searx.be/search"
        params = {
            "q": query,
            "format": "json",
            "language": "en",
            "safesearch": "1",
        }
        response = self._request(endpoint, params=params)
        response.raise_for_status()

        payload = response.json()
        rows = []
        for item in payload.get("results", []):
            title = truncate_text(item.get("title") or "Untitled", 120)
            url = (item.get("url") or "").strip()
            if not url:
                continue
            summary = truncate_text(item.get("content") or item.get("snippet"))
            rows.append({"title": title, "url": url, "summary": summary})
            if len(rows) >= limit:
                break
        return rows

    def _search_duckduckgo(self, query: str, limit: int) -> List[Dict[str, str]]:
        """Use DuckDuckGo HTML endpoint and parse concise result blocks."""
        encoded_query = quote_plus(query)
        endpoint = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        response = self._request(endpoint)
        response.raise_for_status()

        html_text = response.text
        rows = []

        # Parse result titles/links from classic DDG HTML layout.
        pattern = re.compile(
            r'<a[^>]*class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>',
            flags=re.IGNORECASE | re.DOTALL,
        )

        snippets = re.findall(
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>|<div[^>]*class="result__snippet"[^>]*>(.*?)</div>',
            html_text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        parsed_snippets = []
        for s1, s2 in snippets:
            snippet_html = s1 or s2
            parsed_snippets.append(self._strip_html(snippet_html))

        for idx, match in enumerate(pattern.finditer(html_text)):
            url = unescape(match.group("url")).strip()
            title_html = match.group("title")
            title = truncate_text(self._strip_html(title_html), 120)
            if not url:
                continue
            summary = truncate_text(parsed_snippets[idx] if idx < len(parsed_snippets) else "")
            rows.append({"title": title or "Untitled", "url": url, "summary": summary})
            if len(rows) >= limit:
                break

        return rows

    @staticmethod
    def _strip_html(value: str) -> str:
        clean = re.sub(r"<[^>]+>", " ", value)
        clean = unescape(clean)
        return " ".join(clean.split())
