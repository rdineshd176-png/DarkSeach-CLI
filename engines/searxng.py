"""SearXNG JSON search backend."""

import requests

from core.session import PrivacySession
from engines.duckduckgo import DuckDuckGoEngine
from processing.parser import normalize_result


class SearXNGEngine:
    name = "searxng"

    def __init__(self, session: PrivacySession, endpoint: str = "https://searx.be/search"):
        self.session = session
        self.endpoint = endpoint

    def _fetch_payload(self, query: str) -> dict:
        previous_timeout = self.session.config.timeout
        self.session.config.timeout = 8
        try:
            last_error: Exception | None = None
            for _ in range(2):
                try:
                    response = self.session.get(
                        self.endpoint,
                        params={
                            "q": query,
                            "format": "json",
                            "language": "en",
                            "safesearch": "1",
                        },
                    )
                    response.raise_for_status()
                    return response.json()
                except (requests.Timeout, requests.RequestException, ValueError) as exc:
                    last_error = exc
            raise requests.RequestException("SearXNG request failed") from last_error
        finally:
            self.session.config.timeout = previous_timeout

    def search(self, query: str, limit: int = 7) -> list[dict[str, str]]:
        try:
            payload = self._fetch_payload(query)

            rows: list[dict[str, str]] = []
            for item in payload.get("results", []):
                record = normalize_result(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    summary=item.get("content", "") or item.get("snippet", ""),
                    source=self.name,
                )
                if not record["url"]:
                    continue
                rows.append(record)
                if len(rows) >= limit:
                    break
            return rows
        except requests.RequestException:
            print("[WARN] SearXNG failed, falling back to DuckDuckGo")
            return DuckDuckGoEngine(self.session).search(query, limit)
