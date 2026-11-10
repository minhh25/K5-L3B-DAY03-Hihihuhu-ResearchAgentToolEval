"""Unit tests for core tools (CP3 challenge) and the team's new tools.

Offline only: HTTP is mocked with `fake_http`, keys come from `monkeypatch.setenv`.
"""
from __future__ import annotations

import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send = TOOL_FUNCTIONS["send"]
lookup = TOOL_FUNCTIONS["lookup"]
fetch = TOOL_FUNCTIONS["fetch"]
timeline = TOOL_FUNCTIONS["timeline"]
social_search = TOOL_FUNCTIONS["social_search"]
policy = TOOL_FUNCTIONS["policy"]
hackernews = TOOL_FUNCTIONS["hackernews"]
wikipedia = TOOL_FUNCTIONS["wikipedia"]
github_repo = TOOL_FUNCTIONS["github_repo"]
dedupe = TOOL_FUNCTIONS["dedupe"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify(question="Chọn nguồn?", response_type="choice", options=["web", "tweet"])
    assert result["options"] == ["web", "tweet"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [{"title": "1", "section": "A"}, {"title": "2", "section": "B"}, {"title": "3", "section": "A"}]
    markdown = format_tool(items=items, template="sections")["markdown"]
    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [{"title": "một"}, {"title": "hai"}]
    markdown = format_tool(items=items, template="thread")["markdown"]
    assert markdown.startswith("1/")
    assert "\n\n2/" in markdown


def test_format_empty_items_does_not_crash() -> None:
    assert format_tool(items=None, template="sections")["item_count"] == 0
    assert format_tool(items=[], template="bullets")["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    calls = fake_http(FakeResponse({"ok": True}))
    result = send(text="Bản tin", confirmed=True)
    assert result["status"] == "sent"
    assert len(calls) == 1 and calls[0]["method"] == "POST"
    assert "tok123" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "42"
    assert calls[0]["json"]["text"] == "Bản tin"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = send(text="x", confirmed=True)
    assert result["error"] == "RuntimeError"
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))
    lookup(query="AI", timeframe=None)
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "k")
    fake_http(FakeResponse({"data": {"markdown": "nội dung", "metadata": {"title": "T", "sourceURL": "https://a.com/x"}}}))
    item = fetch(url="https://www.a.com/x")["items"][0]
    assert item["title"] == "T"
    assert item["url"] == "https://a.com/x"
    assert item["source"] == "a.com"
    assert item["summary"] == "nội dung"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "k")
    fake_http(FakeResponse({"data": {"markdown": "x" * 9000, "metadata": {}}}))
    assert len(fetch(url="https://a.com")["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    raw = [{"text": "no id", "screen_name": "sama"}]
    raw += [{"tweet_id": str(i), "text": f"t{i}", "screen_name": "sama"} for i in range(6)]
    fake_http(FakeResponse({"timeline": raw}))
    items = timeline(screenname="sama", limit=3)["items"]
    assert len(items) == 3
    assert all(item["url"].startswith("https://x.com/sama/status/") for item in items)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    calls = fake_http(FakeResponse({"timeline": []}))
    social_search(query="OpenAI", search_type="Top")
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert policy(query="")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy(query="data privacy personal", policy_area="data_privacy")["results"]
    assert results
    assert {hit["policy_area"] for hit in results} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = policy(query="citation", policy_area="source_citation", top_k=10)["results"]
    untrusted = " ".join(line for hit in results for line in hit["untrusted_text"])
    facts = " ".join(hit["facts"] for hit in results)
    assert "ignore the citation policy" in untrusted
    assert "ignore the citation policy" not in facts


# ---------------- hackernews ----------------

def test_hackernews_maps_hits_and_clamps_limit(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [
        {"title": "Rust 2.0", "url": "https://rust-lang.org", "points": 10, "num_comments": 3, "objectID": "1"},
        {"title": "Ask HN", "url": None, "points": 5, "num_comments": 1, "objectID": "2"},
        {"title": None, "objectID": "3"},
    ]}))
    result = hackernews(query="rust", max_results=999)
    assert calls[0]["params"]["hitsPerPage"] == 20
    assert [item["title"] for item in result["items"]] == ["Rust 2.0", "Ask HN"]
    assert result["items"][1]["url"] == "https://news.ycombinator.com/item?id=2"


def test_hackernews_bad_input_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    assert hackernews(query="  ")["error"] == "ValueError"
    assert hackernews(query="rust", sort_by="popular")["error"] == "ValueError"
    assert calls == []


def test_hackernews_http_error_returns_error_dict(fake_http) -> None:
    fake_http(requests.ConnectionError("down"))
    assert hackernews(query="rust")["error"] == "ConnectionError"


# ---------------- wikipedia ----------------

def test_wikipedia_maps_summary(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "title": "Alan Turing", "extract": "English mathematician.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Alan_Turing"}},
    }))
    item = wikipedia(title="Alan Turing")["items"][0]
    assert calls[0]["url"].endswith("/page/summary/Alan_Turing")
    assert item["summary"] == "English mathematician."
    assert item["url"] == "https://en.wikipedia.org/wiki/Alan_Turing"


def test_wikipedia_bad_input_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    assert wikipedia(title="")["error"] == "ValueError"
    assert wikipedia(title="X", lang="fr")["error"] == "ValueError"
    assert calls == []


def test_wikipedia_404_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({}, status_code=404))
    assert wikipedia(title="Nope Nope")["error"] == "HTTPError"


# ---------------- github_repo ----------------

def test_github_repo_accepts_url_and_maps_stats(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "full_name": "openai/openai-python", "html_url": "https://github.com/openai/openai-python",
        "description": "SDK", "stargazers_count": 99, "language": "Python", "pushed_at": "2026-01-01",
    }))
    item = github_repo(repo="https://github.com/openai/openai-python/")["items"][0]
    assert calls[0]["url"] == "https://api.github.com/repos/openai/openai-python"
    assert "stars: 99" in item["summary"]


def test_github_repo_malformed_repo_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    for bad in ["", "openai", "a/b/c", "../etc/passwd"]:
        assert github_repo(repo=bad)["error"] == "ValueError"
    assert calls == []


def test_github_repo_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({}, status_code=403))
    assert github_repo(repo="a/b")["error"] == "HTTPError"


# ---------------- dedupe ----------------

def test_dedupe_removes_same_url_and_same_title_ignoring_accents() -> None:
    items = [
        {"title": "A", "url": "https://x.com/1"},
        {"title": "B", "url": "https://X.com/1/"},
        {"title": "Tin Việt", "url": ""},
        {"title": "tin viet"},
    ]
    result = dedupe(items=items)
    assert [item["title"] for item in result["items"]] == ["A", "Tin Việt"]
    assert result["removed"] == 2


def test_dedupe_bad_input_returns_error_dict() -> None:
    assert dedupe(items="not a list")["error"] == "TypeError"
    assert dedupe(items=None)["error"] == "TypeError"


def test_dedupe_skips_non_dict_and_keyless_items() -> None:
    result = dedupe(items=["str", {}, {"title": "ok"}])
    assert result["items"] == [{"title": "ok"}]
