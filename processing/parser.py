"""Result cleaning and normalization helpers."""

from html import unescape
import re
from typing import Dict


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


def normalize_result(title: str, url: str, summary: str, source: str) -> Dict[str, str]:
    return {
        "title": trim_text(strip_html(title), 120) or "Untitled",
        "url": unescape(url or "").strip(),
        "summary": trim_text(strip_html(summary), 240),
        "source": source,
    }
