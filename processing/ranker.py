"""Ranking and deduplication logic for search results."""

from collections import Counter
import re
from urllib.parse import urlparse

TRUST_HINTS = [
    ".gov",
    ".edu",
    "wikipedia.org",
    "arxiv.org",
    "nature.com",
    "ieee.org",
    "who.int",
]


def _normalize_url_key(url: str) -> str:
    parts = urlparse(url)
    netloc = (parts.netloc or "").lower()
    path = (parts.path or "/").rstrip("/")
    return f"{netloc}{path}"


def _title_fingerprint(title: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", (title or "").lower())
    return " ".join(tokens[:10])


def deduplicate(results: list[dict[str, str]]) -> list[dict[str, str]]:
    seen_urls = set()
    seen_titles = set()
    unique_rows = []
    for row in results:
        url_key = _normalize_url_key(row.get("url", ""))
        title_key = _title_fingerprint(row.get("title", ""))

        if not url_key:
            continue

        # Drop exact URL duplicates and near-title duplicates to reduce noisy repeats.
        if url_key in seen_urls or (title_key and title_key in seen_titles):
            continue

        seen_urls.add(url_key)
        if title_key:
            seen_titles.add(title_key)
        unique_rows.append(row)
    return unique_rows


def score_result(result: dict[str, str], query: str) -> float:
    query_terms = [token for token in query.lower().split() if token]
    title = result.get("title", "").lower()
    summary = result.get("summary", "").lower()
    url = result.get("url", "").lower()

    title_tokens = title.split()
    summary_tokens = summary.split()
    term_counter = Counter(title_tokens + summary_tokens)

    keyword_hits = sum(term_counter.get(term, 0) for term in query_terms)
    title_relevance = sum(1 for term in query_terms if term in title) * 1.5
    trust_bonus = 3.0 if any(hint in url for hint in TRUST_HINTS) else 0.0
    summary_depth = min(len(summary_tokens) / 80.0, 1.5)

    return keyword_hits + title_relevance + trust_bonus + summary_depth


def rank_results(results: list[dict[str, str]], query: str) -> list[dict[str, str]]:
    unique_rows = deduplicate(results)
    for row in unique_rows:
        row["rank_score"] = round(score_result(row, query), 3)

    return sorted(unique_rows, key=lambda r: r.get("rank_score", 0.0), reverse=True)
