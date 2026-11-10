from __future__ import annotations

from typing import Any

from tools._shared import err, terms

POSITIVE_WORDS = {
    "tot", "hay", "thich", "tuyet", "ngon",
    "good", "great", "excellent", "love", "amazing", "awesome", "positive",
}
NEGATIVE_WORDS = {
    "te", "xau", "chan", "kem",
    "bad", "terrible", "awful", "hate", "poor", "disappointing", "negative",
}


def analyze_sentiment(text: str = "") -> dict[str, Any]:
    try:
        if not isinstance(text, str):
            raise TypeError(f"text must be a string, got {type(text).__name__}")
        tokens = terms(text)
        positive_hits = sorted(tokens & POSITIVE_WORDS)
        negative_hits = sorted(tokens & NEGATIVE_WORDS)
        if len(positive_hits) > len(negative_hits):
            label = "positive"
        elif len(negative_hits) > len(positive_hits):
            label = "negative"
        else:
            label = "neutral"
        return {
            "tool": "sentiment",
            "text": text,
            "label": label,
            "positive_hits": positive_hits,
            "negative_hits": negative_hits,
        }
    except Exception as exc:
        return err("sentiment", exc)
