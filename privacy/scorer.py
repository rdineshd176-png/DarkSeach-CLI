"""Privacy scoring for discovered links."""

from urllib.parse import parse_qs, urlparse

TRACKER_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "msclkid",
    "adid",
    "ref",
}


def score_url(url: str) -> int:
    """Compute simple privacy score from 1 to 10 for a given URL."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    query_keys = {key.lower() for key in parse_qs(parsed.query).keys()}

    score = 10
    if parsed.scheme != "https":
        score -= 2

    tracker_count = sum(1 for key in query_keys if key in TRACKER_KEYS or key.startswith("utm_"))
    score -= min(tracker_count, 4)

    if any(word in host for word in ["ads", "doubleclick", "tracker", "analytics"]):
        score -= 2

    return max(1, min(10, score))


def attach_privacy_scores(results: list[dict[str, str]]) -> list[dict[str, str]]:
    for row in results:
        row["privacy_score"] = score_url(row.get("url", ""))
    return results
