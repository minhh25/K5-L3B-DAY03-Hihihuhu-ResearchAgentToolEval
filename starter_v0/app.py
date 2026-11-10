from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="centered")

PROVIDER_NAME = "openrouter"
VERSION_LABEL = "v4c"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4


@st.cache_resource
def get_agent_config() -> dict[str, Any]:
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(PROVIDER_NAME)
    selected_model = getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(VERSION_LABEL, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    return {
        "system_prompt": system_prompt,
        "openai_tools": openai_tools,
        "provider": provider,
        "model": selected_model,
        "artifact_version": artifact_version,
    }


def init_session_state(config: dict[str, Any]) -> None:
    if "history" in st.session_state:
        return
    st.session_state.history = []
    st.session_state.display_turns = []
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(VERSION_LABEL), safe_slug(PROVIDER_NAME), timestamp])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(config["artifact_version"]),
        "provider": PROVIDER_NAME,
        "model": config["model"],
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": HISTORY_WINDOW,
        "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant"):
        st.write(turn["assistant_text"])
        tool_events = turn.get("tool_events") or []
        if tool_events:
            with st.expander(f"🔧 {len(tool_events)} tool call(s)"):
                for event in tool_events:
                    st.markdown(f"**{event['tool']}**`({event['args']})`")
                    st.json(event["result"])


def main() -> None:
    config = get_agent_config()
    init_session_state(config)

    st.title("🔎 Research Agent")
    st.caption(
        "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, phân tích cảm xúc nội dung, "
        "tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."
    )

    with st.sidebar:
        st.markdown("### Thông tin phiên")
        st.write(f"Provider: `{PROVIDER_NAME}`")
        st.write(f"Model: `{config['model']}`")
        st.write(f"Artifact version: `{config['artifact_version'].artifact_version}`")
        st.markdown("### Câu hỏi mẫu")
        st.markdown(
            "- Tìm tin AI hôm nay có gì nổi bật?\n"
            "- Lấy 5 tweet mới nhất của Elon Musk\n"
            "- Tóm tắt bài viết này giúp mình (chưa đưa URL — xem agent hỏi lại)\n"
            "- Đăng bản tin này lên Telegram giúp mình\n"
            "- Tìm tin AI hôm nay, rồi phân tích cảm xúc bài đó giúp mình"
        )
        if st.button("🧹 Xoá hội thoại / bắt đầu transcript mới"):
            for key in ("history", "display_turns", "transcript", "transcript_path"):
                st.session_state.pop(key, None)
            st.rerun()

    for turn in st.session_state.display_turns:
        render_turn(turn)

    user_text = st.chat_input("Nhập yêu cầu của bạn...")
    if not user_text:
        return

    messages = [
        {"role": "system", "content": config["system_prompt"]},
        *trim_history(st.session_state.history, HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.spinner("Agent đang xử lý..."):
        try:
            result = run_model_tool_loop(
                provider=config["provider"],
                messages=messages,
                tools=config["openai_tools"],
                model=config["model"],
                max_tool_rounds=MAX_TOOL_ROUNDS,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            st.session_state.history.append({"role": "user", "content": user_text})
            st.session_state.history.append({"role": "assistant", "content": assistant_text})
        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "assistant_text": f"Lỗi: {type(exc).__name__}: {exc}",
                "error": f"{type(exc).__name__}: {exc}",
            })

    turn_record["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    st.session_state.display_turns.append(turn_record)

    st.rerun()


if __name__ == "__main__":
    main()
