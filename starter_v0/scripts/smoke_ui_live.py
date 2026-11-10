"""Live UI check: real provider + local source filtering; never clicks send."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
    if app.exception:
        raise RuntimeError('Streamlit startup failed; inspect local AppTest output')
    prompt = ('Lọc cục bộ bằng filter_sources, không truy cập web: chỉ giữ domain example.org '
              'trong [{"url":"https://example.org/a"},{"url":"https://example.net/b"}]. '
              'Trả lời ngắn với URL đã giữ.')
    app.chat_input[0].set_value(prompt).run(timeout=240)
    transcript = app.session_state['transcript']
    turn = transcript['turns'][-1] if transcript['turns'] else {}
    selected = [event for event in turn.get('tool_events', []) if event['tool'] == 'filter_sources']
    passed = (not app.exception and turn.get('status') == 'answered' and
              any(event.get('result', {}).get('items') == [{'url': 'https://example.org/a', 'source': 'example.org'}]
                  for event in selected))
    result = {
        'check': 'Real Streamlit AppTest with live provider; no fake provider or HTTP mocks',
        'passed': passed, 'provider': transcript['provider'], 'model': transcript['model'],
        'artifact_version': transcript['artifact_version'], 'status': turn.get('status'),
        'transcript': f"transcripts/{transcript['transcript_id']}.transcript.json",
        'assistant_text': turn.get('assistant_text'),
        'tool_names': [event['tool'] for event in turn.get('tool_events', [])],
        'external_send_clicked': False,
    }
    (ROOT / 'analysis/ui_live.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
