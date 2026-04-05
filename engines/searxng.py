"""SearXNG JSON search backend."""

from core.session import PrivacySession
from processing.parser import normalize_result


class SearXNGEngine:
    name = "searxng"

    def __init__(self, session: PrivacySession, endpoint: str = "https://searx.be/search"):
        self.session = session
        self.endpoint = endpoint

    def search(self, query: str, limit: int = 7) -> list[dict[str, str]]:
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
        payload = response.json()

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
