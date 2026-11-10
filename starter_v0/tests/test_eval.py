"""Regression checks for structured args and resumable, quota-aware evidence."""
import json
import sys
from pathlib import Path

import pytest

import run_eval
from providers.base import ModelResponse, ToolCall


def test_structured_item_arguments_compare_without_dict_sort_error():
    expected = {'items': [{'url': 'https://example.org/a', 'title': 'A'}, {'url': 'https://example.org/b', 'title': 'B'}]}
    actual = {'items': list(reversed(expected['items']))}
    assert run_eval.compare_subset(expected, actual) == (True, [], 1, 1)
    actual['items'] = [{'url': 'https://wrong.org'}]
    assert run_eval.compare_subset(expected, actual)[0] is False


def test_quota_halt_and_resume_preserve_measured_cases(monkeypatch, tmp_path):
    dataset = tmp_path / 'cases.json'
    dataset.write_text(json.dumps({'cases': [
        {'id': 'S1', 'phase': 'B', 'query': 'Capabilities?', 'failure_type': 'unnecessary_tool', 'expect': {'no_tool': True}},
        {'id': 'S2', 'phase': 'B', 'query': 'Filter empty sources', 'failure_type': 'wrong_tool', 'expect': {'tool_calls': [{'name': 'filter_sources', 'args': {'items': []}}]}},
        {'id': 'S3', 'phase': 'B', 'query': 'Capabilities again?', 'failure_type': 'unnecessary_tool', 'expect': {'no_tool': True}},
    ]}))
    prompt = tmp_path / 'prompt.md'; prompt.write_text('Test research agent')
    base_args = ['run_eval.py', '--provider', 'openrouter', '--model', 'test-free-model', '--version', 'v3', '--suite', 'group',
                 '--eval-cases', str(dataset), '--system-prompt', str(prompt), '--runs-dir', str(tmp_path / 'runs')]

    class Provider:
        def __init__(self, fail):
            self.calls = 0
            self.fail = fail

        def complete(self, *args, **kwargs):
            self.calls += 1
            if self.fail and self.calls == 2:
                raise RuntimeError('free-models-per-day')
            if not self.fail and self.calls == 1:
                return ModelResponse(tool_calls=[ToolCall('filter_sources', {'items': []})])
            return ModelResponse(text='Research capabilities')

    first = Provider(True)
    monkeypatch.setattr(run_eval, 'make_provider', lambda name: first)
    monkeypatch.setattr(sys, 'argv', base_args)
    run_eval.main()
    original_path = next((tmp_path / 'runs').glob('*.json'))
    original_bytes = original_path.read_bytes()
    original = json.loads(original_bytes)
    assert first.calls == 2
    assert original['summary']['measured_cases'] == 1
    assert original['results'][2]['result']['execution_status'] == 'not_executed_quota'

    second = Provider(False)
    monkeypatch.setattr(run_eval, 'make_provider', lambda name: second)
    monkeypatch.setattr(sys, 'argv', base_args + ['--resume-from', str(original_path)])
    run_eval.main()
    new_path = next(p for p in (tmp_path / 'runs').glob('*.json') if p != original_path)
    resumed = json.loads(new_path.read_text())
    assert second.calls == 2
    assert resumed['summary']['passed_cases'] == resumed['summary']['total_cases'] == 3
    assert resumed['summary']['provider_error_cases'] == 0
    assert resumed['results'][0]['reused_from'] == original['run_id']
    assert original_path.read_bytes() == original_bytes

    prompt.write_text('Changed artifact')
    with pytest.raises(SystemExit, match='prompt_hash changed'):
        run_eval.main()


def test_group_cases_have_required_distribution_and_tool_coverage():
    data = json.loads((run_eval.DATA_DIR / 'eval_group.json').read_text())
    cases = data['cases']
    assert len(cases) == len({c['id'] for c in cases}) == 10
    assert sum('query' in c for c in cases) == sum('turns' in c for c in cases) == 5
    assert all(c['phase'] == 'B' and c['metadata']['what_it_tests'] for c in cases)
    run_eval.validate_case_failure_types(cases, Path('eval_group.json'))
    assert any(call['name'] == 'filter_sources' for c in cases for call in c['expect'].get('tool_calls', []))
