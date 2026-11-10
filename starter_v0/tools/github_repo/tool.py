from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def github_repo_info(repo: str = "") -> dict[str, Any]:
    try:
        repo = (repo or "").strip().removeprefix("https://github.com/").strip("/")
        if not _REPO.match(repo):
            raise ValueError("repo must look like 'owner/name'")
        response = requests.get(f"https://api.github.com/repos/{repo}", timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return {
            "tool": "github_repo_info",
            "items": [{
                "title": data.get("full_name"),
                "url": data.get("html_url"),
                "source": "github.com",
                "summary": f"{data.get('description') or ''} | stars: {data.get('stargazers_count')} | "
                           f"language: {data.get('language')} | updated: {data.get('pushed_at')}",
            }],
        }
    except Exception as exc:
        return err("github_repo_info", exc)
