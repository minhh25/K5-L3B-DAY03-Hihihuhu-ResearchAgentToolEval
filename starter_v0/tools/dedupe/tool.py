from __future__ import annotations

from typing import Any

from tools._shared import err, fold_text


def dedupe_items(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    try:
        if not isinstance(items, list):
            raise TypeError("items must be a list of objects")
        seen: set[str] = set()
        kept: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            key = (item.get("url") or "").rstrip("/").lower() or fold_text(item.get("title") or "").strip()
            if not key or key in seen:
                continue
            seen.add(key)
            kept.append(item)
        return {"tool": "dedupe_items", "items": kept, "removed": len(items) - len(kept)}
    except Exception as exc:
        return err("dedupe_items", exc)
