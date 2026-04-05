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
    corpus = " ".join(
        f"{row.get('title', '')}. {row.get('summary', '')}" for row in results[:8]
    )
    tokens = _tokenize(corpus)
    top_keywords = [word for word, _ in Counter(tokens).most_common(8)]

    sentences = _split_sentences(corpus)
    keyword_set = set(top_keywords)

    ranked_sentences = sorted(
        sentences,
        key=lambda line: sum(1 for token in _tokenize(line) if token in keyword_set),
        reverse=True,
    )
    chosen = ranked_sentences[:3] if ranked_sentences else ["No meaningful summary could be generated."]

    avg_privacy = 0.0
    if results:
        avg_privacy = sum(float(row.get("privacy_score", 0)) for row in results) / len(results)

    return {
        "key_topic": query.strip() or "General research",
        "keywords": top_keywords,
        "summary": " ".join(chosen),
        "insights": [
            f"Top result count analyzed: {min(len(results), 8)}",
            f"Average privacy score: {avg_privacy:.1f}/10",
            f"Most common keyword: {top_keywords[0] if top_keywords else 'N/A'}",
        ],
    }
