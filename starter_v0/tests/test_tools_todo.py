"""Offline tool challenge: verify real transformations, requests and failure paths."""
from __future__ import annotations

import copy
import importlib

import pytest
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


def test_clarify_choice_returns_options_and_awaits_user():
    result = TOOL_FUNCTIONS['clarify']('Nguồn nào?', 'choice', ['web', 'X'])
    assert result['options'] == ['web', 'X']
    assert result['awaiting_user'] is True
    assert result['response_type'] == 'choice'


def test_format_sections_groups_items_by_section():
    result = TOOL_FUNCTIONS['format'](items=[{'section': s, 'title': s} for s in ['A', 'B', 'A']], template='sections')
    assert result['markdown'].count('## A') == result['markdown'].count('## B') == 1
    assert result['item_count'] == 3


def test_format_thread_numbers_items():
    result = TOOL_FUNCTIONS['format']([{'title': 'Một'}, {'title': 'Hai'}], 'thread')
    assert [p.split(' ', 1)[0] for p in result['markdown'].split('\n\n')] == ['1/', '2/']


@pytest.mark.parametrize('items', [None, []])
def test_format_empty_items_does_not_crash(items):
    result = TOOL_FUNCTIONS['format'](items)
    assert result['item_count'] == 0
    assert result['markdown'] == ''


def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http):
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'fake-token')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', 'private-test')
    calls = fake_http(FakeResponse({'ok': True}))
    assert TOOL_FUNCTIONS['send']('Bản tin', True)['status'] == 'sent'
    assert len(calls) == 1
    assert calls[0]['method'] == 'POST'
    assert calls[0]['url'] == 'https://api.telegram.org/botfake-token/sendMessage'
    assert calls[0]['json'] == {'chat_id': 'private-test', 'text': 'Bản tin', 'parse_mode': 'Markdown'}


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http):
    calls = fake_http(FakeResponse())
    assert TOOL_FUNCTIONS['send']('Tin', True)['error'] == 'RuntimeError'
    assert not calls


def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http):
    monkeypatch.setenv('TAVILY_API_KEY', 'fake-key')
    calls = fake_http(FakeResponse({'results': []}))
    assert TOOL_FUNCTIONS['lookup']('robotics', timeframe=None)['items'] == []
    assert 'time_range' not in calls[0]['json']


def test_fetch_maps_firecrawl_response(monkeypatch, fake_http):
    monkeypatch.setenv('FIRECRAWL_API_KEY', 'fake-key')
    calls = fake_http(FakeResponse({'data': {'markdown': 'Body', 'metadata': {'title': 'T', 'sourceURL': 'https://example.com/final'}}}))
    result = TOOL_FUNCTIONS['fetch']('https://example.com/start')
    assert calls[0]['json'] == {'url': 'https://example.com/start', 'formats': ['markdown']}
    assert result['items'] == [{'title': 'T', 'url': 'https://example.com/final', 'source': 'example.com', 'summary': 'Body'}]


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http):
    monkeypatch.setenv('FIRECRAWL_API_KEY', 'fake-key')
    fake_http(FakeResponse({'data': {'markdown': 'x' * 5000}}))
    assert TOOL_FUNCTIONS['fetch']('https://example.com')['items'][0]['summary'] == 'x' * 4000


def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http):
    monkeypatch.setenv('RAPIDAPI_KEY', 'fake-key')
    calls = fake_http(FakeResponse({'timeline': [{'text': 'no id'}] + [
        {'tweet_id': str(i), 'screen_name': 'researcher', 'text': f'Post {i}'} for i in range(1, 7)]}))
    result = TOOL_FUNCTIONS['timeline']('researcher', 3)
    assert [i['url'] for i in result['items']] == [f'https://x.com/researcher/status/{i}' for i in range(1, 4)]
    assert calls[0]['params']['screenname'] == 'researcher'


@pytest.mark.parametrize('sort', ['Top', 'Latest'])
def test_social_search_passes_search_type(monkeypatch, fake_http, sort):
    monkeypatch.setenv('RAPIDAPI_KEY', 'fake-key')
    calls = fake_http(FakeResponse({'tweets': []}))
    assert TOOL_FUNCTIONS['social_search']('robotics', sort)['items'] == []
    assert calls[0]['params'] == {'query': 'robotics', 'search_type': sort}


def test_policy_empty_query_returns_no_results():
    assert TOOL_FUNCTIONS['policy']('')['results'] == []


def test_policy_area_filter_only_returns_that_area():
    result = TOOL_FUNCTIONS['policy']('privacy data', 'data_privacy')
    assert result['results']
    assert all(i['policy_area'] == 'data_privacy' for i in result['results'])


def test_policy_instruction_like_lines_go_to_untrusted_text():
    result = TOOL_FUNCTIONS['policy']('source citation', 'source_citation', top_k=20)
    untrusted = [line for i in result['results'] for line in i['untrusted_text']]
    assert untrusted
    assert any('ignore' in line.lower() or 'bỏ qua' in line.lower() for line in untrusted)
    assert all(line not in i['facts'] for i in result['results'] for line in untrusted)


def test_filter_sources_normalizes_deduplicates_and_filters_without_mutation():
    items = [
        {'url': 'https://WWW.Example.com:443/a?utm_source=x#part', 'score': .8, 'title': 'A'},
        {'url': 'https://example.com/a', 'score': .9},
        {'url': 'https://news.example.com/b', 'score': .7},
        {'url': 'https://evilexample.com/b', 'score': 1},
        {'url': 'https://example.com/c', 'score': .1},
    ]
    before = copy.deepcopy(items)
    result = TOOL_FUNCTIONS['filter_sources'](items, ['example.com'], ['news.example.com'], .5)
    assert result['items'] == [{'url': 'https://example.com/a', 'score': .8, 'title': 'A', 'source': 'example.com'}]
    assert result['removed_count'] == 4
    assert items == before


@pytest.mark.parametrize('kwargs', [
    {'items': 'wrong'}, {'items': [None]}, {'limit': -1}, {'limit': True},
    {'min_score': float('nan')}, {'min_score': '0.5'}, {'include_domains': ['https://example.com']},
    {'exclude_domains': 'example.com'}, {'include_domains': ['bad..com']},
])
def test_filter_sources_bad_input_from_model_returns_error(kwargs):
    assert TOOL_FUNCTIONS['filter_sources'](**kwargs)['error'] == 'ValueError'


def test_filter_sources_failure_returns_error_dict(monkeypatch):
    module = importlib.import_module('tools.filter_sources.tool')
    def broken(value):
        raise OSError('normalizer unavailable')
    monkeypatch.setattr(module, '_normalize_url', broken)
    result = module.filter_sources([{'url': 'https://example.com/a'}])
    assert result['error'] == 'OSError'
    assert result['message'] == 'normalizer unavailable'


@pytest.mark.parametrize('items', [None, []])
def test_filter_sources_empty_data(items):
    result = TOOL_FUNCTIONS['filter_sources'](items)
    assert result['items'] == []
    assert result['input_count'] == result['kept_count'] == result['removed_count'] == 0


def test_filter_sources_zero_limit_and_invalid_urls():
    items = [{'url': u} for u in ['javascript:alert(1)', 'https://user:pass@example.com', 'https://example.com:bad', 'https://example.com/a']]
    assert TOOL_FUNCTIONS['filter_sources'](items)['kept_count'] == 1
    result = TOOL_FUNCTIONS['filter_sources'](items, limit=0)
    assert result['items'] == [] and result['removed_count'] == 4


def test_filter_sources_preserves_meaningful_query_and_subdomains():
    result = TOOL_FUNCTIONS['filter_sources']([
        {'url': 'https://docs.example.com/search?q=agent&utm_medium=ref'},
        {'url': 'https://docs.example.com/search?q=tools'},
    ], include_domains=['example.com'])
    assert [i['url'] for i in result['items']] == ['https://docs.example.com/search?q=agent', 'https://docs.example.com/search?q=tools']


def test_send_timeout_does_not_expose_token(monkeypatch, fake_http):
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'fake-secret-token')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', 'private-test')
    fake_http(requests.Timeout('https://api.telegram.org/botfake-secret-token/sendMessage'))
    result = TOOL_FUNCTIONS['send']('Tin', True)
    assert result['error'] == 'Timeout'
    assert 'fake-secret-token' not in str(result)


@pytest.mark.parametrize('confirmed', ['false', 'true', 1, [], {}])
def test_send_requires_literal_boolean_confirmation(confirmed, fake_http):
    calls = fake_http(FakeResponse({'ok': True}))
    result = TOOL_FUNCTIONS['send']('Tin', confirmed)
    assert result['status'] == 'needs_confirmation'
    assert not calls


def test_send_api_rejection_is_not_reported_as_sent(monkeypatch, fake_http):
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'fake-token')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', 'private-test')
    fake_http(FakeResponse({'ok': False, 'description': 'bad request'}))
    assert TOOL_FUNCTIONS['send']('Tin', True)['error'] == 'RuntimeError'
