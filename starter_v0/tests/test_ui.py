"""Streamlit AppTest uses a fake provider but the real model/tool loop."""
from pathlib import Path

from streamlit.testing.v1 import AppTest
from providers.base import ModelResponse, ToolCall
from test_chat import ScriptedProvider

APP = Path(__file__).resolve().parents[1] / 'app.py'


def setup_app(monkeypatch, provider):
    import providers
    import chat
    monkeypatch.setattr(providers, 'make_provider', lambda name: provider)
    monkeypatch.setattr(chat, 'write_transcript', lambda path, data: None)
    return AppTest.from_file(str(APP)).run(timeout=20)


def test_ui_runs_real_loop_displays_sources_and_clears_history(monkeypatch):
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall('filter_sources', {'items': [{'url': 'https://example.com/a'}]})]),
        ModelResponse(text='Nguồn https://example.com/a'),
    ])
    app = setup_app(monkeypatch, provider)
    assert not app.exception
    app.chat_input[0].set_value('Lọc nguồn').run(timeout=20)
    assert not app.exception
    assert app.session_state['transcript']['turns'][0]['tool_events'][0]['tool'] == 'filter_sources'
    assert any('https://example.com/a' in m.value for m in app.markdown)
    next(b for b in app.button if b.label == 'Xóa cuộc trò chuyện').click().run()
    assert app.session_state['transcript']['turns'] == []


def test_ui_surfaces_provider_errors(monkeypatch):
    class Broken:
        def complete(self, *args, **kwargs):
            raise RuntimeError('provider unavailable')
    app = setup_app(monkeypatch, Broken())
    app.chat_input[0].set_value('Tin mới').run(timeout=20)
    assert not app.exception
    assert app.error
    assert 'chưa xử lý được' in app.error[0].value
    assert any('provider unavailable' in block.value for block in app.code)
    assert app.session_state['transcript']['turns'][0]['status'] == 'provider_error'


def test_ui_clarifies_missing_account(monkeypatch):
    provider = ScriptedProvider([ModelResponse(tool_calls=[ToolCall('clarify', {'question': 'Bạn muốn đọc tài khoản nào?'})])])
    app = setup_app(monkeypatch, provider)
    app.chat_input[0].set_value('Đọc feed').run(timeout=20)
    assert not app.exception
    turn = app.session_state['transcript']['turns'][0]
    assert turn['status'] == 'waiting_for_user'
    assert 'tài khoản nào' in turn['assistant_text']


def test_ui_sends_only_after_preview_button_and_does_not_replay(monkeypatch):
    import chat
    calls = []
    monkeypatch.setitem(chat.TOOL_FUNCTIONS, 'send', lambda **kwargs: calls.append(kwargs) or {'status': 'sent'})
    app = setup_app(monkeypatch, ScriptedProvider([]))
    app.text_area[0].set_value('Bản tin đã duyệt').run()
    next(b for b in app.button if b.label == 'Xem trước bản gửi').click().run()
    assert not calls
    assert app.session_state['pending_send'] == 'Bản tin đã duyệt'
    next(b for b in app.button if b.label == 'Xác nhận gửi').click().run()
    assert not app.exception
    assert calls == [{'text': 'Bản tin đã duyệt', 'confirmed': True}]
    assert app.session_state['pending_send'] is None
    app.run()
    assert len(calls) == 1
    assert app.session_state['transcript']['turns'][0]['approval_source'] == 'explicit_ui_button'


def test_ui_quick_start_submits_once_without_replaying_after_rerun(monkeypatch):
    provider = ScriptedProvider([ModelResponse(text='Bạn gửi URL bài viết nhé.')])
    app = setup_app(monkeypatch, provider)
    next(b for b in app.button if b.label == 'Tóm tắt bài viết').click().run(timeout=20)
    assert not app.exception
    assert len(provider.messages) == 1
    assert 'Hãy hỏi mình URL trước' in provider.messages[0][-1]['content']
    assert len(app.session_state['transcript']['turns']) == 1
    app.run()
    assert not app.exception
    assert len(provider.messages) == 1


def test_ui_quota_error_explains_limit_and_keeps_diagnostic_detail(monkeypatch):
    class QuotaLimited:
        def complete(self, *args, **kwargs):
            raise RuntimeError('429 free-models-per-day')
    app = setup_app(monkeypatch, QuotaLimited())
    app.chat_input[0].set_value('Tin hôm nay').run(timeout=20)
    assert not app.exception
    assert 'hết lượt trong ngày' in app.error[0].value
    assert any('free-models-per-day' in block.value for block in app.code)
    assert app.session_state['transcript']['turns'][0]['status'] == 'provider_error'
