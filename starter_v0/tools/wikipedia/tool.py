from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err


def wikipedia_summary(title: str = "", lang: str = "en") -> dict[str, Any]:
    try:
        title = (title or "").strip()
        if not title:
            raise ValueError("title is empty")
        if lang not in {"en", "vi"}:
            raise ValueError("lang must be 'en' or 'vi'")
        response = requests.get(
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}",
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        url = (data.get("content_urls") or {}).get("desktop", {}).get("page", "")
        return {
            "tool": "wikipedia_summary",
            "items": [{
                "title": data.get("title"),
                "url": url,
                "source": f"{lang}.wikipedia.org",
                "summary": data.get("extract"),
            }],
        }
    except Exception as exc:
        return err("wikipedia_summary", exc)
