"""Append measured evidence; never infer a score from a label or overwrite rows."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def record(run_path: Path, changed: str, hypothesis: str, before: str, reason: str, *, record_incomplete: bool = False):
    data = json.loads(run_path.read_text())
    summary = data['summary']
    valid = summary['provider_error_cases'] == 0 and summary['measured_cases'] == summary['total_cases']
    if not valid and not record_incomplete:
        raise ValueError('Run không hợp lệ; giữ JSON nhưng không đưa vào bảng điểm')
    for key, field in [('system_prompt', 'prompt_hash'), ('tools', 'tools_hash')]:
        path = Path(data[key])
        if not path.is_absolute():
            path = ROOT / path
        if hashlib.sha256(path.read_bytes()).hexdigest() != data[field]:
            raise ValueError(f'Artifact thay đổi sau khi đo: {path}')
    log = ROOT / 'artifacts/version_log.csv'
    with log.open(newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader); fields = reader.fieldnames
    if any(row['version'] == data['version'] and row['run_file'] == str(run_path.relative_to(ROOT)) for row in rows):
        raise ValueError('Run đã được ghi')
    row = dict.fromkeys(fields, '')
    row.update(version=data['version'], author='Chưa cung cấp danh tính', changed_artifact=changed,
               artifact_version=data['artifact_version'], prompt_hash=data['prompt_hash'], tools_hash=data['tools_hash'],
               reason=('' if valid else f"INVALID — measured={summary['measured_cases']}/{summary['total_cases']}, provider_error={summary['provider_error_cases']}; ") + reason + '; model=' + data['model'], hypothesis=hypothesis,
               metric_before=before, metric_after=str(summary['case_accuracy']) if valid else '', run_file=str(run_path.relative_to(ROOT)))
    with log.open('a', newline='') as f:
        csv.DictWriter(f, fields, lineterminator='\n').writerow(row)
    print(data['version'], summary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('--changed', required=True)
    parser.add_argument('--hypothesis', required=True)
    parser.add_argument('--before', default='')
    parser.add_argument('--reason', default='')
    parser.add_argument('--record-incomplete', action='store_true', help='Log an INVALID attempt with blank metric_after; never treat it as a score')
    args = parser.parse_args()
    record(args.run.resolve(), args.changed, args.hypothesis, args.before, args.reason, record_incomplete=args.record_incomplete)
