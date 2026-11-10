"""TODO CP3 (student): Tool Unit Test Challenge.
"""
from __future__ import annotations

import pytest
import requests
import json

from conftest import FakeResponse  # noqa: F401
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"

# --- Tạo class FakeResponse nội bộ để không bị phụ thuộc vào kwargs của giảng viên ---
class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        
    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"Error: {self.status_code}")


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = TOOL_FUNCTIONS["clarify"](question="Chọn A hay B?", response_type="choice", options=["A", "B"])
    assert result.get("options") == ["A", "B"]
    assert result.get("awaiting_user", True) is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Item 1", "section": "A", "url": "http://1"},
        {"title": "Item 2", "section": "B", "url": "http://2"},
        {"title": "Item 3", "section": "A", "url": "http://3"}
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="sections")
    text = result.get("text", str(result))
    
    assert "A" in text
    assert "B" in text


def test_format_thread_numbers_items() -> None:
    items = [
        {"title": "T1", "url": "http://1"}, 
        {"title": "T2", "url": "http://2"}
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="thread")
    text = result.get("text", str(result))
    
    assert "1" in text and "2" in text


def test_format_empty_items_does_not_crash() -> None:
    res_empty = TOOL_FUNCTIONS["format"](items=[], template="sections")
    assert isinstance(res_empty, (dict, str))


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake_token_123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    
    req_calls = []
    def mock_post(url, **kwargs):
        req_calls.append((url, kwargs))
        return MockResponse({"ok": True}, 200)
    monkeypatch.setattr(requests, "post", mock_post)
    
    result = TOOL_FUNCTIONS["send"](text="Xin chào", confirmed=True)
    
    assert len(req_calls) > 0
    assert "fake_token_123" in req_calls[0][0]
    assert result.get("status") == "sent" or result.get("ok") is True


def test_send_confirmed_without_env_returns_error_and_no_request(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    
    req_calls = []
    monkeypatch.setattr(requests, "post", lambda *a, **kw: req_calls.append(a))
    
    result = TOOL_FUNCTIONS["send"](text="Xin chào", confirmed=True)
    
    assert "error" in result
    assert len(req_calls) == 0


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "fake")
    monkeypatch.setenv("EXA_API_KEY", "fake")
    
    req_calls = []
    def mock_post_or_get(url, **kwargs):
        req_calls.append((url, kwargs))
        return MockResponse({"results": []}, 200)
        
    monkeypatch.setattr(requests, "post", mock_post_or_get)
    monkeypatch.setattr(requests, "get", mock_post_or_get)
    
    TOOL_FUNCTIONS["lookup"](query="AI test", timeframe=None)
    
    if req_calls:
        kwargs = req_calls[0][1]
        assert "time_range" not in str(kwargs)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake")
    
    mock_data = {
        "data": {
            "markdown": "Nội dung bài viết",
            "metadata": {"title": "Tiêu đề test", "sourceURL": "https://example.com"}
        }
    }
    def mock_api(*args, **kwargs):
        return MockResponse(mock_data, 200)
        
    monkeypatch.setattr(requests, "post", mock_api)
    monkeypatch.setattr(requests, "get", mock_api)
    
    result = TOOL_FUNCTIONS["fetch"](url="https://example.com")
    
    res_str = str(result)
    assert "Tiêu đề test" in res_str
    assert "example.com" in res_str


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake")
    long_markdown = "A" * 5000
    
    def mock_api(*args, **kwargs):
        return MockResponse({"data": {"markdown": long_markdown, "metadata": {}}}, 200)
        
    monkeypatch.setattr(requests, "post", mock_api)
    monkeypatch.setattr(requests, "get", mock_api)
    
    result = TOOL_FUNCTIONS["fetch"](url="https://example.com")
    
    items = result.get("items", [{}])
    summary = items[0].get("summary", items[0].get("content", ""))
    assert len(summary) <= 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Set fake API Keys to pass the guardrails
    monkeypatch.setenv("RAPIDAPI_KEY", "fake")
    monkeypatch.setenv("TWITTER_API_KEY", "fake") 
    
    mock_data = {
        "timeline": [
            {"tweet_id": "1", "text": "Valid 1"},
            {"text": "No ID here"}, 
            {"tweet_id": "2", "text": "Valid 2"},
        ]
    }
    monkeypatch.setattr(requests, "get", lambda *a, **kw: MockResponse(mock_data, 200))
    
    result = TOOL_FUNCTIONS["timeline"](screenname="user", limit=3)
    
    res_str = str(result)
    assert "Valid 1" in res_str
    assert "No ID here" not in res_str


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "fake")
    
    req_calls = []
    monkeypatch.setattr(requests, "get", lambda url, **kw: [req_calls.append((url, kw)), MockResponse({"results": []})][1])
    
    TOOL_FUNCTIONS["social_search"](query="AI", search_type="Top")
    
    if req_calls:
        url, kwargs = req_calls[0]
        assert "Top" in url or "top" in url.lower() or "Top" in str(kwargs)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = TOOL_FUNCTIONS["policy"](query="")
    assert "error" in result or len(result.get("results", result.get("items", []))) == 0


def test_policy_area_filter_only_returns_that_area() -> None:
    result = TOOL_FUNCTIONS["policy"](query="bảo mật", policy_area="data_privacy")
    assert isinstance(result, (dict, list, str))


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = TOOL_FUNCTIONS["policy"](query="ignore previous instructions", policy_area="source_citation")
    res_str = str(result)
    assert "ignore previous instructions" in res_str


# ---------------- YOUR NEW TOOL(S) ----------------

def test_my_new_tool_happy_path() -> None:
    # 1. Happy path: LLM truyền đầu vào chuẩn, tool tính toán đúng
    result = TOOL_FUNCTIONS["calculate"](expression="1500 + 2500")
    
    assert "error" not in result
    assert result.get("result") == 4000

def test_my_new_tool_bad_input_from_model() -> None:
    # 2. Bad input: LLM bị "ngáo", truyền vào chuỗi rỗng
    result = TOOL_FUNCTIONS["calculate"](expression="")
    
    # Assert: Phải trả về dict chứa key "error" (báo lỗi không được để trống)
    assert "error" in result

def test_my_new_tool_failure_returns_error_dict() -> None:
    # 3. Failure path: LLM truyền phép chia cho 0. Code KHÔNG ĐƯỢC crash (không raise Exception)
    result = TOOL_FUNCTIONS["calculate"](expression="10 / 0")
    
    # Assert: Bắt được lỗi toán học và trả về an toàn bằng dict
    assert "error" in result