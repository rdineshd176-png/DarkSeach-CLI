"""Result cleaning and normalization helpers."""

from html import unescape
import re
from typing import Any, Dict
from urllib.parse import parse_qs, unquote, urlparse


def strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", text or "")
    clean = unescape(clean)
    return " ".join(clean.split())


def trim_text(text: str, max_len: int = 240) -> str:
    if not text:
        return "No summary available."
    compact = " ".join(text.split())
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 3].rstrip() + "..."


def clean_result_url(url: str) -> tuple[str, bool]:
    """Return cleaned destination URL and whether an intermediate redirect was detected."""
    raw = unescape((url or "").strip())
    if not raw:
        return "", False

    parsed = urlparse(raw)
    query = parse_qs(parsed.query)

    # DuckDuckGo redirect format: /l/?uddg=<encoded destination>
    if "duckduckgo.com" in (parsed.netloc or "").lower() and parsed.path.startswith("/l/"):
        candidate = query.get("uddg", [""])[0]
        if candidate:
            return unquote(candidate), True

    # Generic redirect parameters seen in search/result aggregator links.
    for key in ("uddg", "url", "u", "target", "redirect", "dest"):
        candidate = query.get(key, [""])[0]
        if candidate.startswith("http://") or candidate.startswith("https://"):
            return unquote(candidate), True

    return raw, False


def normalize_result(title: str, url: str, summary: str, source: str) -> Dict[str, Any]:
    clean_url, had_redirect = clean_result_url(url)
    return {
        "title": trim_text(strip_html(title), 120) or "Untitled",
        "url": clean_url,
        "summary": trim_text(strip_html(summary), 240),
        "source": source,
        # Keep redirect trace to power privacy scoring heuristics.
        "had_redirect": had_redirect,
    }
