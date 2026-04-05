"""DuckDuckGo HTML search backend."""

import re
from urllib.parse import quote_plus

from core.session import PrivacySession
from processing.parser import normalize_result


class DuckDuckGoEngine:
    name = "duckduckgo"

    def __init__(self, session: PrivacySession):
        self.session = session

    def search(self, query: str, limit: int = 7) -> list[dict[str, str]]:
        encoded = quote_plus(query.strip())
        endpoint = f"https://html.duckduckgo.com/html/?q={encoded}"
        response = self.session.get(endpoint)
        response.raise_for_status()

        html_text = response.text
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
            record = normalize_result(
                title=match.group("title"),
                url=match.group("url"),
                summary=snippets[idx] if idx < len(snippets) else "",
                source=self.name,
            )
            if not record["url"]:
                continue
            rows.append(record)
            if len(rows) >= limit:
                break

        return rows
