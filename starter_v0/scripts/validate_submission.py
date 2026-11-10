"""Offline integrity, evidence, schema and secret checks. No network or writes."""
from __future__ import annotations

import csv
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from env_loader import load_lab_env
from tools import TOOL_FUNCTIONS, load_tool_declarations


def check_submission() -> dict:
    reference = json.loads((ROOT / 'artifacts/baseline_integrity.json').read_text())
    checks = {}
    for label, path, digest in [
        ('baseline_v0', ROOT / reference['baseline_file'], reference['sha256']),
        ('eval_base_unchanged', ROOT / 'data/eval_base.json', reference['eval_base_sha256']),
        ('eval_extension_unchanged', ROOT / 'data/eval_research_extension.json', reference['eval_extension_sha256']),
    ]:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, label
        checks[label] = True

    declarations = load_tool_declarations(ROOT / 'artifacts/tools.yaml')
    assert {d['name'] for d in declarations} == set(TOOL_FUNCTIONS)
    for declaration in declarations:
        params = declaration['parameters']
        assert set(params['properties']) <= set(inspect.signature(TOOL_FUNCTIONS[declaration['name']]).parameters)
        assert set(params.get('required', [])) <= set(params['properties'])
    checks['registry_schema'] = True
    group = json.loads((ROOT / 'data/eval_group.json').read_text())['cases']
    assert len(group) == len({c['id'] for c in group}) == 10
    assert sum('query' in c for c in group) == sum('turns' in c for c in group) == 5
    assert all(c['metadata']['what_it_tests'] for c in group)
    checks['group_5_single_5_multi'] = True

    with (ROOT / 'artifacts/version_log.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == 'version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_before,metric_after,run_file'.split(',')
        rows = list(reader)
    accepted, incomplete = [], []
    accepted_suites = set()
    for row in rows:
        assert None not in row
        run = json.loads((ROOT / row['run_file']).read_text())
        for field in ['artifact_version', 'prompt_hash', 'tools_hash']:
            assert run[field] == row[field]
        for artifact, field in [('system_prompt.md', 'prompt_hash'), ('tools.yaml', 'tools_hash')]:
            path = ROOT / 'artifacts/versions' / f"{row['version']}_{artifact}"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == run[field]
        summary = run['summary']
        valid = summary['provider_error_cases'] == 0 and summary['measured_cases'] == summary['total_cases']
        if valid:
            assert float(row['metric_after']) == summary['case_accuracy']
            accepted.append(run['run_id'])
            accepted_suites.add((run['version'], run['suite']))
        else:
            assert row['metric_after'] == '' and row['reason'].startswith('INVALID')
            incomplete.append(run['run_id'])
    assert {'v0', 'v1', 'v2', 'v3'} <= {row['version'] for row in rows}
    checks['csv_hashes_and_validity'] = True

    report = (ROOT.parent / 'report/team/group_report.md').read_text()
    for section in ['## 1.', '## 2.', '## 3.', '## 4.', '## 5.', '## 6.', '## 7.', '## 8.', '### A1.', '### A2.', '### A3.',
                    '### B1.', '### B2.', '### B3.', '### B4.', '### B5a.', '### B5.', '### B7.']:
        assert section in report, section
    checks['official_report_sections'] = True

    load_lab_env(ROOT)
    names = ['OPENROUTER_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY',
             'TAVILY_API_KEY', 'FIRECRAWL_API_KEY', 'RAPIDAPI_KEY', 'TELEGRAM_BOT_TOKEN']
    secret_values = [os.environ[n].encode() for n in names if os.environ.get(n) and len(os.environ[n]) >= 8
                     and not any(x in os.environ[n].lower() for x in ['your-', 'your_', '<your', 'replace_me'])]
    paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT.parent).split(b'\0')
    scanned = 0
    for relative in paths:
        if not relative:
            continue
        path = ROOT.parent / os.fsdecode(relative)
        assert not (path.name == '.env' or path.name == 'secrets.toml'), 'Credential file is not ignored'
        if path.is_file():
            content = path.read_bytes()
            assert not any(value in content for value in secret_values), f'Secret exposure in {path.relative_to(ROOT.parent)}'
            scanned += 1
    checks['secret_scan'] = {'ok': True, 'files_scanned': scanned, 'checked': 'Exact configured secret values; not a universal secret detector'}
    pending = []
    for version, suite in [('v2', 'base'), ('v3', 'base'), ('v3', 'group')]:
        if (version, suite) not in accepted_suites:
            pending.append(f'Valid {version}/{suite} eval still needed')
    # Count actual successful model-loop turns, excluding local commands and
    # turns explicitly marked not executed after quota exhaustion.
    live = []
    for path in sorted((ROOT / 'transcripts').glob('*.transcript.json')):
        transcript = json.loads(path.read_text())
        turns = [turn for turn in transcript.get('turns', [])
                 if turn.get('status') in {'answered', 'waiting_for_user'} and turn.get('rounds')]
        if len(turns) >= 3:
            live.append(str(path.relative_to(ROOT)))
    if not live:
        pending.append('At least 3 successful live model turns still needed')
    pending += ['Public deployment', 'Member identities and personal verification', 'User-owned commits, push and LMS submission']
    return {'checks': checks, 'accepted_runs': accepted, 'incomplete_runs': incomplete,
            'live_transcripts_with_at_least_3_model_turns': live,
            'live_scenario_review': 'Review B4 for research, clarification/fill and send confirmation; turn count alone does not grade behavior',
            'pending': pending}


if __name__ == '__main__':
    print(json.dumps(check_submission(), ensure_ascii=False, indent=2))
