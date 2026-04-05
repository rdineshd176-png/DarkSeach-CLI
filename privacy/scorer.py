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

    # HTTP links leak metadata more often than HTTPS.
    if parsed.scheme != "https":
        score -= 3

    if any(key in TRACKER_KEYS or key.startswith("utm_") for key in query_keys):
        score -= 2

    if any(word in host for word in ["ads", "tracking", "click", "redirect"]):
        score -= 1

    return max(1, min(10, score))


def score_result(result: dict[str, object]) -> int:
    """Compute privacy score using both URL and parser metadata."""
    score = score_url(str(result.get("url", "")))

    if bool(result.get("had_redirect", False)):
        score -= 2

    return max(1, min(10, score))


def attach_privacy_scores(results: list[dict[str, object]]) -> list[dict[str, object]]:
    for row in results:
        row["privacy_score"] = score_result(row)
    return results
