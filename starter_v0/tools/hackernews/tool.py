from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

HN_SORTS = {"relevance": "search", "date": "search_by_date"}


def search_hackernews(query: str = "", sort_by: str = "relevance", max_results: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query is empty")
        if sort_by not in HN_SORTS:
            raise ValueError(f"sort_by must be one of {sorted(HN_SORTS)}")
        limit = max(1, min(int(max_results or 5), 20))
        response = requests.get(
            f"https://hn.algolia.com/api/v1/{HN_SORTS[sort_by]}",
            params={"query": query, "tags": "story", "hitsPerPage": limit},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items = [{
            "title": hit.get("title"),
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            "source": "news.ycombinator.com",
            "summary": f"{hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments",
        } for hit in response.json().get("hits", []) if hit.get("title")]
        return {"tool": "search_hackernews", "query": query, "sort_by": sort_by, "items": items}
    except Exception as exc:
        return err("search_hackernews", exc)
