"""Local research workspace, backed by the same live model/tool loop as the CLI."""
from __future__ import annotations

from datetime import datetime
from html import escape
import json
import os
from time import perf_counter
from urllib.parse import urlsplit

import streamlit as st

from chat import (
    ARTIFACTS_DIR, ROOT, confirm_send, confirmation_id, history_assistant,
    now_iso, run_model_tool_loop, trim_history, write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


SEARCH = '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>'
BOOK = '<path d="M4 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-3H4z"/><path d="M13 7a3 3 0 0 1 3-3h5v14h-4a4 4 0 0 0-4 3"/>'
SOURCES = '<path d="M5 5h14M5 12h10M5 19h6"/><circle cx="19" cy="17" r="3"/><path d="m21 19 2 2"/>'
TOOL_LABELS = {
    'lookup': 'Tìm kiếm trên web', 'fetch': 'Đọc bài viết', 'format': 'Tạo bản tóm tắt',
    'filter_sources': 'Lọc và sắp xếp nguồn', 'timeline': 'Đọc bài đăng của tài khoản',
    'social_search': 'Tìm bài đăng trên X', 'clarify': 'Hỏi thêm thông tin',
    'send': 'Chuẩn bị gửi bản tin', 'policy': 'Tra tài liệu nội bộ',
    'papers': 'Tìm bài báo khoa học', 'paper_text': 'Đọc bài báo khoa học',
}
STARTERS = [
    ('news', SEARCH, '', 'Tìm tin mới', 'Cập nhật một chủ đề, kèm link để bạn đọc thêm.',
     'Tìm trên web 3 tin về AI hôm nay, trả lời ngắn bằng tiếng Việt và kèm link nguồn.'),
    ('article', BOOK, 'amber', 'Tóm tắt bài viết', 'Đọc nhanh ý chính từ một đường link bạn cung cấp.',
     'Mình muốn tóm tắt một bài viết. Hãy hỏi mình URL trước nhé.'),
    ('sources', SOURCES, 'blue', 'Sắp xếp nguồn', 'Lọc theo tên miền và bỏ các đường link trùng nhau.',
     'Lọc cục bộ bằng filter_sources, chỉ giữ domain example.org và bỏ link trùng: '
     '[{"url":"https://example.org/a"},{"url":"https://example.org/a?utm_source=demo"},'
     '{"url":"https://example.net/b"}]. Trả lời ngắn bằng tiếng Việt.'),
]


def svg(paths: str, size: int = 22) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{paths}</svg>')


def queue_prompt(prompt: str) -> None:
    st.session_state.queued_prompt = prompt


def source_links(events: list[dict]) -> str:
    """Show only real HTTP(S) source URLs, with escaped labels and attributes."""
    links, seen = [], set()
    for event in events:
        result = event.get('result', {})
        if not isinstance(result, dict):
            continue
        items = result.get('items') or []
        if not isinstance(items, list):
            continue
        for item in items:
            url = item.get('url') if isinstance(item, dict) else None
            if not isinstance(url, str) or any(ord(c) < 32 for c in url):
                continue
            try:
                parsed = urlsplit(url)
                if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
                    continue
                host = parsed.hostname.removeprefix('www.')
            except ValueError:
                continue
            if url in seen:
                continue
            seen.add(url)
            links.append(f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
                         f'{escape(host)} <span aria-hidden="true">↗</span></a>')
    return '<div class="desk-sources">' + ''.join(links[:6]) + '</div>' if links else ''


def error_message(error: str) -> str:
    lower = error.lower()
    if 'free-models-per-day' in lower:
        return 'Mô hình miễn phí đã hết lượt trong ngày. Bạn có thể thử lại khi hạn mức được làm mới hoặc dùng kết nối khác còn hạn mức.'
    if '429' in lower or 'rate limit' in lower:
        return 'Mô hình đang giới hạn yêu cầu. Bạn chờ một chút rồi thử lại nhé.'
    if '401' in lower or 'api key' in lower or 'authentication' in lower:
        return 'Kết nối chưa được xác thực. Bạn kiểm tra API key trong cấu hình trên máy rồi thử lại nhé.'
    return 'Mình chưa xử lý được yêu cầu này. Bạn kiểm tra kết nối hoặc thử lại sau nhé.'


st.set_page_config(page_title='Research Desk · Hihihuhu', page_icon='🔎', layout='wide', initial_sidebar_state='auto')
st.markdown((ROOT / 'ui/style.css').read_text(encoding='utf-8'), unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="desk-brand"><div class="desk-brand-mark">' + svg(SEARCH, 23) +
                '</div><div><div class="desk-brand-name">Research Desk</div>'
                '<div class="desk-brand-sub">HIHIHUHU · RESEARCH ASSISTANT</div></div></div>', unsafe_allow_html=True)
    clear = st.button('Xóa cuộc trò chuyện', icon=':material/add:', use_container_width=True,
                      help='Bắt đầu một cuộc trò chuyện mới.')
    st.markdown('<div class="desk-nav-label">KHÔNG GIAN CỦA BẠN</div>', unsafe_allow_html=True)
    st.caption('Tìm nguồn, đọc bài và cùng làm rõ những điều bạn đang quan tâm.')
    with st.expander('Cài đặt kết nối', icon=':material/tune:'):
        provider_name = st.selectbox('Provider', ['openrouter', 'openai', 'anthropic', 'gemini', 'ollama'])
        default_model = ('nvidia/nemotron-3.5-lightning:free' if provider_name == 'openrouter'
                         else getattr(make_provider(provider_name), 'default_model', ''))
        model = st.text_input('Model', value=default_model, key=f'model_{provider_name}')
        max_rounds = st.slider('Số bước xử lý tối đa', 1, 8, 4, help='Tăng khi yêu cầu cần tìm, đọc và tổng hợp qua nhiều bước.')
        st.caption('API key được đọc từ .env hoặc biến môi trường trên máy. Đổi provider/model sẽ mở phiên mới.')
    with st.expander('Gửi bản tin Telegram', icon=':material/send:'):
        st.caption('Soạn nội dung, xem lại rồi xác nhận khi bạn muốn gửi.')
        draft = st.text_area('Nội dung gửi lên kênh riêng', key='telegram_draft', height=130)
        preview = st.button('Xem trước bản gửi', disabled=not draft.strip(), use_container_width=True)
    with st.expander('Mẹo sử dụng', icon=':material/lightbulb:'):
        st.markdown('- Nêu chủ đề, khoảng thời gian và số kết quả bạn cần.\n'
                    '- Dán URL để đọc và tóm tắt một bài cụ thể.\n'
                    '- Hỏi tiếp hoặc sửa yêu cầu ngay trong khung chat.')

config = (provider_name, model)
if clear or 'transcript' not in st.session_state or st.session_state.get('config') != config:
    st.session_state.config = config
    st.session_state.history = []
    st.session_state.pending_send = st.session_state.pending_id = None
    st.session_state.pop('queued_prompt', None)
    stamp = datetime.now().strftime('%Y%m%dT%H%M%S%f')
    version = build_artifact_version('v3', ARTIFACTS_DIR / 'system_prompt.md', ARTIFACTS_DIR / 'tools.yaml')
    st.session_state.transcript = {
        'transcript_id': f'v3_ui_{stamp}', **artifact_version_dict(version),
        'provider': provider_name, 'model': model, 'interface': 'streamlit', 'ui_revision': 'friendly-local-v1',
        'system_prompt': str(ARTIFACTS_DIR / 'system_prompt.md'), 'tools': str(ARTIFACTS_DIR / 'tools.yaml'),
        'history_window': 5, 'max_tool_rounds': max_rounds, 'created_at': now_iso(), 'updated_at': now_iso(), 'turns': [],
    }
transcript = st.session_state.transcript
if preview:
    st.session_state.pending_send = draft
    st.session_state.pending_id = confirmation_id(draft)


def save_turn(user: str, result: dict, *, started_at: str | None = None) -> None:
    turn = {'turn_index': len(transcript['turns']) + 1, 'started_at': started_at or now_iso(),
            'ended_at': now_iso(), 'user': user, 'max_tool_rounds': max_rounds, **result}
    transcript['turns'].append(turn)
    st.session_state.history.extend([{'role': 'user', 'content': user},
                                     {'role': 'assistant', 'content': history_assistant(result)}])
    write_transcript(ROOT / 'transcripts' / f"{transcript['transcript_id']}.transcript.json", transcript)


def display_turn(turn: dict) -> None:
    with st.chat_message('user', avatar=':material/person:'):
        st.write(turn['user'])
    with st.chat_message('assistant', avatar=':material/travel_explore:'):
        status = turn.get('status')
        if status in {'provider_error', 'tool_error'}:
            detail = turn.get('error') or turn.get('assistant_text') or 'Không có thông tin lỗi.'
            st.error(error_message(detail))
            with st.expander('Chi tiết lỗi'):
                st.code(detail, language=None)
        elif status == 'max_tool_rounds':
            st.warning('Yêu cầu đã đến giới hạn xử lý. Bạn thử chia thành các bước nhỏ hơn hoặc tăng số bước trong Cài đặt kết nối nhé.')
        else:
            st.markdown(turn.get('assistant_text') or 'Mình chưa nhận được nội dung trả lời. Bạn thử hỏi lại nhé.')
        events = turn.get('tool_events', [])
        for event in events:
            result = event.get('result', {})
            if isinstance(result, dict) and result.get('error'):
                label = TOOL_LABELS.get(event['tool'], 'Xử lý nguồn')
                st.warning(f"{label} chưa thành công. Bạn có thể xem lý do trong Các bước đã thực hiện bên dưới.")
        sources = source_links(events)
        if sources:
            st.markdown(sources, unsafe_allow_html=True)
        if events:
            with st.expander(f'Các bước đã thực hiện · {len(events)}'):
                for index, event in enumerate(events, 1):
                    st.markdown(f"**{index}. {TOOL_LABELS.get(event['tool'], 'Xử lý yêu cầu')}**")
                    st.json(event)
        if status == 'waiting_for_user':
            confirmation = any(e['tool'] in {'send', 'clarify'} and
                               (e.get('args', {}).get('response_type') == 'yes_no' or e['tool'] == 'send') for e in events)
            st.caption('Chờ bạn xác nhận' if confirmation else 'Bạn bổ sung thông tin ngay bên dưới nhé')
        elif status == 'answered':
            duration = turn.get('duration_seconds')
            st.caption(f'Đã trả lời · {duration:g} giây' if duration is not None else 'Đã trả lời')


st.markdown('<div class="desk-topbar"><span>Không gian làm việc &nbsp;/&nbsp; <b>Nghiên cứu</b></span>'
            '<span class="desk-local">● &nbsp; Demo trên máy của bạn</span></div>', unsafe_allow_html=True)
if not transcript['turns']:
    st.markdown('<div class="desk-hero"><div class="desk-orbit">' + svg(SEARCH, 29) + '</div>'
                '<div class="desk-eyebrow">TÒ MÒ MỘT CHÚT. HIỂU THÊM MỘT CHÚT.</div>'
                '<h1>Bạn muốn tìm hiểu<br>điều gì hôm nay?</h1>'
                '<p>Tìm tin mới, đọc bài viết và tổng hợp nguồn thông tin. '
                'Mình sẽ hỏi lại nếu cần bạn bổ sung thêm.</p>'
                '<div class="desk-pills"><span>Có link nguồn</span><span>Hỏi tiếp tự nhiên</span>'
                '<span>Bạn duyệt trước khi gửi</span></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="desk-starter-label">CHỌN MỘT GỢI Ý ĐỂ BẮT ĐẦU</div>', unsafe_allow_html=True)
    for column, (key, paths, color, label, description, prompt) in zip(st.columns(3, gap='medium'), STARTERS):
        with column, st.container(border=True, key=f'starter_{key}'):
            st.markdown(f'<div class="desk-card-icon {color}">{svg(paths)}</div>', unsafe_allow_html=True)
            st.button(label, key=f'quick_{key}', on_click=queue_prompt, args=(prompt,), use_container_width=True)
            st.markdown(f'<p class="desk-card-description">{description}</p>', unsafe_allow_html=True)
    st.markdown('<div class="desk-help">Hoặc nhập câu hỏi của riêng bạn vào khung chat bên dưới.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="desk-chat-title"><h1>Cùng làm rõ điều bạn cần biết.</h1>'
                '<p>Bạn có thể hỏi tiếp, bổ sung nguồn hoặc điều chỉnh yêu cầu.</p></div>', unsafe_allow_html=True)
    for turn in transcript['turns']:
        display_turn(turn)

if st.session_state.pending_send is not None:
    with st.container(border=True, key='send_confirmation'):
        st.subheader('Xem lại trước khi gửi')
        st.caption('Nội dung bên dưới sẽ được gửi nguyên văn lên kênh Telegram đã cấu hình khi bạn xác nhận.')
        st.code(st.session_state.pending_send, language=None)
        approve_col, cancel_col = st.columns(2)
        if approve_col.button('Xác nhận gửi', type='primary', use_container_width=True):
            text, digest = st.session_state.pending_send, st.session_state.pending_id
            st.session_state.pending_send = st.session_state.pending_id = None
            with st.spinner('Đang gửi nội dung bạn đã duyệt…'):
                sent = confirm_send(text, digest)
            save_turn('[Xác nhận gửi bản xem trước]', {
                'status': sent.get('status', 'tool_error'),
                'assistant_text': 'Đã gửi bản tin lên Telegram.' if sent.get('status') == 'sent' else json.dumps(sent, ensure_ascii=False),
                'approval_source': 'explicit_ui_button', 'confirmation_id': digest, 'rounds': [],
                'tool_events': [{'tool': 'send', 'args': {'text': text, 'confirmed': True}, 'result': sent}],
            })
            st.rerun()
        if cancel_col.button('Hủy gửi', use_container_width=True):
            st.session_state.pending_send = st.session_state.pending_id = None
            st.rerun()

typed_prompt = st.chat_input('Hỏi điều bạn muốn biết, hoặc dán một đường link…', key='research_input')
queued_prompt = st.session_state.pop('queued_prompt', None)
user_text = typed_prompt or queued_prompt
if user_text:
    st.session_state.pending_send = st.session_state.pending_id = None
    started_at, started_clock = now_iso(), perf_counter()
    with st.chat_message('user', avatar=':material/person:'):
        st.write(user_text)
    try:
        version = build_artifact_version('v3', ARTIFACTS_DIR / 'system_prompt.md', ARTIFACTS_DIR / 'tools.yaml')
        if version.artifact_version != transcript['artifact_version']:
            raise RuntimeError('Prompt/tools đã thay đổi. Hãy xóa cuộc trò chuyện để bắt đầu phiên mới.')
        messages = [{'role': 'system', 'content': (ARTIFACTS_DIR / 'system_prompt.md').read_text(encoding='utf-8')},
                    *trim_history(st.session_state.history, 5), {'role': 'user', 'content': user_text}]
        with st.chat_message('assistant', avatar=':material/travel_explore:'):
            with st.spinner('Mình đang đọc và xử lý yêu cầu của bạn…'):
                result = run_model_tool_loop(
                    provider=make_provider(provider_name), messages=messages,
                    tools=to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / 'tools.yaml')),
                    model=model, max_tool_rounds=max_rounds,
                )
        if result.get('pending_send'):
            st.session_state.pending_send = result['pending_send']
            st.session_state.pending_id = confirmation_id(result['pending_send'])
    except Exception as exc:
        result = {'status': 'provider_error', 'error': f'{type(exc).__name__}: {exc}',
                  'assistant_text': 'Chưa xử lý được yêu cầu.', 'rounds': [], 'tool_events': []}
    result['duration_seconds'] = round(perf_counter() - started_clock, 1)
    save_turn(user_text, result, started_at=started_at)
    st.rerun()

with st.sidebar:
    key_name = {'openrouter': 'OPENROUTER_API_KEY', 'openai': 'OPENAI_API_KEY',
                'anthropic': 'ANTHROPIC_API_KEY', 'gemini': 'GEMINI_API_KEY'}.get(provider_name)
    configured = provider_name == 'ollama' or bool(os.getenv(key_name or ''))
    connection = 'Đã có cấu hình kết nối' if configured else 'Chưa có API key trên máy'
    st.markdown(f'<div class="desk-connection"><strong><i class="desk-dot"></i>{escape(provider_name.title())}</strong>'
                f'<span>{connection}</span></div>', unsafe_allow_html=True)
    st.download_button('Tải cuộc trò chuyện', json.dumps(transcript, ensure_ascii=False, indent=2),
                       file_name=f"{transcript['transcript_id']}.transcript.json", mime='application/json',
                       icon=':material/download:', use_container_width=True)
    st.caption('Research Desk · Hihihuhu\n\nNguồn và các bước xử lý luôn có thể xem lại.')
