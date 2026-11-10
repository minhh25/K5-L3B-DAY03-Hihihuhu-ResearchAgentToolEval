"""Offline runtime tests; fake model, real tool implementations, no external writes."""
from providers.base import ModelResponse, ToolCall
from tools import TOOL_FUNCTIONS
from agent import ResearchAgent
from chat import confirmation_id, confirm_send, history_assistant, run_model_tool_loop, trim_history


class ScriptedProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.messages = []

    def complete(self, messages, tools=None, **kwargs):
        self.messages.append(list(messages))
        return next(self.responses)


def loop(provider, rounds=4):
    return run_model_tool_loop(provider=provider, messages=[{'role': 'user', 'content': 'test'}], tools=[], model=None, max_tool_rounds=rounds)


def test_runtime_preserves_sources_for_next_model_round_and_history():
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall('filter_sources', {'items': [{'url': 'https://example.com/a'}]})]),
        ModelResponse(text='Nguồn: https://example.com/a'),
    ])
    result = loop(provider)
    assert result['status'] == 'answered'
    assert 'https://example.com/a' in provider.messages[1][-1]['content']
    assert 'PRIOR_TOOL_RESULTS_JSON' in history_assistant(result)
    assert 'https://example.com/a' in history_assistant(result)


def test_clarify_pauses_entire_batch_before_any_other_tool(monkeypatch):
    calls = []
    monkeypatch.setitem(TOOL_FUNCTIONS, 'lookup', lambda **kwargs: calls.append(kwargs))
    result = loop(ScriptedProvider([ModelResponse(tool_calls=[
        ToolCall('lookup', {'query': 'should not run'}),
        ToolCall('clarify', {'question': 'Tài khoản nào?'}),
        ToolCall('send', {'text': 'should not send', 'confirmed': True}),
    ])]))
    assert not calls
    assert result['status'] == 'waiting_for_user'
    assert [e['tool'] for e in result['tool_events']] == ['clarify']


def test_model_cannot_self_authorize_send(monkeypatch):
    calls = []
    monkeypatch.setitem(TOOL_FUNCTIONS, 'send', lambda **kwargs: calls.append(kwargs))
    result = loop(ScriptedProvider([ModelResponse(tool_calls=[ToolCall('send', {'text': 'Preview', 'confirmed': True})])]))
    assert not calls
    assert result['pending_send'] == 'Preview'
    assert result['status'] == 'waiting_for_user'


def test_explicit_confirmation_is_bound_to_exact_preview(monkeypatch):
    calls = []
    monkeypatch.setitem(TOOL_FUNCTIONS, 'send', lambda **kwargs: calls.append(kwargs) or {'status': 'sent'})
    digest = confirmation_id('Original')
    assert confirm_send('Changed', digest)['error'] == 'invalid_confirmation'
    assert not calls
    assert confirm_send('Original', digest)['status'] == 'sent'
    assert calls == [{'text': 'Original', 'confirmed': True}]


def test_eval_scores_send_proposal_without_executing_it(monkeypatch):
    calls = []
    monkeypatch.setitem(TOOL_FUNCTIONS, 'send', lambda **kwargs: calls.append(kwargs))
    result = ResearchAgent(ScriptedProvider([ModelResponse(tool_calls=[ToolCall('send', {'text': 'No', 'confirmed': True})])]), system_prompt='test').run([])
    assert result.tool_calls[0].name == 'send'
    assert result.tool_results[0]['result']['status'] == 'blocked_in_eval'
    assert not calls


def test_runtime_reports_tool_error_instead_of_losing_it():
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall('fetch', {'url': 'https://example.com'})]),
        ModelResponse(text='Không đọc được nguồn.'),
    ])
    result = loop(provider)
    assert result['tool_events'][0]['result']['error'] == 'RuntimeError'
    assert 'FIRECRAWL_API_KEY' in provider.messages[1][-1]['content']


def test_runtime_stops_when_model_keeps_calling_tools():
    result = loop(ScriptedProvider([ModelResponse(tool_calls=[ToolCall('filter_sources', {'items': []})])]), rounds=1)
    assert result['status'] == 'max_tool_rounds'
    assert len(result['rounds']) == 1


def test_history_window_retains_whole_pairs():
    history = [{'role': r, 'content': str(i)} for i in range(4) for r in ['user', 'assistant']]
    assert trim_history(history, 2) == history[-4:]
    assert trim_history(history, 0) == []
