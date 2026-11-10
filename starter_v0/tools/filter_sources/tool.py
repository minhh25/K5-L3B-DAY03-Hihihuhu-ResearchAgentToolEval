"""Deterministic filtering of supplied research sources; no network or file writes."""
from __future__ import annotations

import math
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from tools._shared import err


def _domains(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError("Domain criteria must be arrays of hostnames")
    result = []
    for value in values:
        if not isinstance(value, str):
            raise ValueError("Each domain must be a hostname string")
        host = value.strip().lower().removeprefix("www.").rstrip(".")
        if not host or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789.-" for c in host):
            raise ValueError("Use a hostname without scheme, path or port")
        if any(not part or part.startswith("-") or part.endswith("-") for part in host.split(".")):
            raise ValueError("Invalid hostname")
        result.append(host)
    return result


def _normalize_url(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, str):
        return None
    try:
        parts = urlsplit(value.strip())
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
            return None
        host = parts.hostname.lower().removeprefix("www.").rstrip(".")
        host = _domains([host])[0]
        port = parts.port  # also validates malformed ports
        netloc = host if port is None or (parts.scheme.lower(), port) in {("http", 80), ("https", 443)} else f"{host}:{port}"
        query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                 if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
        return urlunsplit((parts.scheme.lower(), netloc, parts.path or "/", urlencode(query), "")), host
    except ValueError:
        return None


def filter_sources(
    items: list[dict[str, Any]] | None = None,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    min_score: float = 0.0,
    limit: int = 20,
) -> dict[str, Any]:
    """Keep valid HTTP(S) sources in input order; exclude wins; deduplicate URLs."""
    try:
        if items is None:
            items = []
        if not isinstance(items, list) or len(items) > 1000 or any(not isinstance(i, dict) for i in items):
            raise ValueError("items must be an array of at most 1000 objects")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= 1000:
            raise ValueError("limit must be an integer from 0 to 1000")
        if isinstance(min_score, bool) or not isinstance(min_score, (int, float)) or not math.isfinite(min_score) or not 0 <= min_score <= 1:
            raise ValueError("min_score must be a finite number from 0 to 1")
        included, excluded = _domains(include_domains), _domains(exclude_domains)
        selected: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in items:
            normalized = _normalize_url(item.get("url"))
            if normalized is None:
                continue
            url, host = normalized
            matches = lambda domains: any(host == d or host.endswith("." + d) for d in domains)
            if (included and not matches(included)) or matches(excluded):
                continue
            score = item.get("score", 0)
            if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 1 or score < min_score:
                continue
            if url in seen:
                continue
            seen.add(url)
            selected.append({**item, "url": url, "source": host})
        result = selected[:limit]
        return {"tool": "filter_sources", "items": result, "input_count": len(items),
                "kept_count": len(result), "removed_count": len(items) - len(result)}
    except Exception as exc:
        return err("filter_sources", exc)
