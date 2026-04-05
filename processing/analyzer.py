"""Keyword and sentence-based analysis without external AI APIs."""

import re
from collections import Counter

STOPWORDS = {
    "the",
    "and",
    "with",
    "from",
    "that",
    "this",
    "into",
    "have",
    "your",
    "about",
    "what",
    "when",
    "where",
    "which",
    "while",
    "using",
    "through",
    "their",
    "there",
    "been",
    "were",
    "will",
    "than",
    "then",
    "them",
    "they",
    "http",
    "https",
    "www",
    "com",
    "org",
    "results",
    "result",
    "research",
    "search",
    "page",
}


def _tokenize(text: str) -> list[str]:
    return [
        word
        for word in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
        if word not in STOPWORDS
    ]


def _split_sentences(text: str) -> list[str]:
    rows = re.split(r"(?<=[.!?])\s+", text.strip())
    return [line.strip() for line in rows if line.strip()]


def analyze_results(query: str, results: list[dict[str, str]]) -> dict[str, object]:
    top_rows = results[:8]
    corpus = " ".join(f"{row.get('title', '')}. {row.get('summary', '')}" for row in top_rows)
    tokens = _tokenize(corpus)
    frequencies = Counter(tokens)
    top_keywords = [word for word, _ in frequencies.most_common(8)]

    sentences = []
    for row in top_rows:
        sentences.extend(_split_sentences(row.get("summary", "")))
    keyword_set = set(top_keywords)

    ranked_sentences = sorted(
        sentences,
        key=lambda line: (
            sum(1 for token in _tokenize(line) if token in keyword_set),
            len(line),
        ),
        reverse=True,
    )
    chosen = ranked_sentences[:3] if ranked_sentences else ["No meaningful summary could be generated."]

    avg_privacy = 0.0
    if results:
        avg_privacy = sum(float(row.get("privacy_score", 0)) for row in results) / len(results)

    key_topic = query.strip() or "General research"
    if not query.strip() and top_keywords:
        key_topic = " / ".join(top_keywords[:2])

    trusted_sources = sum(1 for row in top_rows if float(row.get("privacy_score", 0)) >= 8)

    return {
        "key_topic": key_topic,
        "keywords": top_keywords,
        "summary": " ".join(chosen),
        "insights": [
            f"Top result count analyzed: {len(top_rows)}",
            f"Average privacy score: {avg_privacy:.1f}/10",
            f"Most common keyword: {top_keywords[0] if top_keywords else 'N/A'}",
            f"Higher-privacy sources (>=8/10): {trusted_sources}/{len(top_rows) if top_rows else 0}",
        ],
    }
