from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from chat import ARTIFACTS_DIR, ROOT, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("🔎 Research Agent")

with st.sidebar:
    provider_name = st.selectbox("Provider", ["gemini", "openrouter", "openai", "anthropic", "ollama"])
    version = st.text_input("Version label", "v4")
    if st.button("Reset chat"):
        st.session_state.clear()
        st.rerun()

prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"

if "history" not in st.session_state:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    artifact = build_artifact_version(version, prompt_path, tools_path)
    st.session_state.history = []
    st.session_state.display = []
    st.session_state.transcript_path = ROOT / "transcripts" / f"{safe_slug(version)}_{provider_name}_{stamp}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": st.session_state.transcript_path.stem,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "source": "streamlit",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "turns": [],
    }

for role, text, events in st.session_state.display:
    with st.chat_message(role):
        st.markdown(text)
        for event in events:
            with st.expander(f"🔧 {event['tool']}"):
                st.code(json.dumps({"args": event["args"], "result": event["result"]}, ensure_ascii=False, indent=2, default=str)[:4000], language="json")

user_text = st.chat_input("Hỏi gì đó, ví dụ: Tweet mới nhất của Sam Altman?")
if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)
    messages = [
        {"role": "system", "content": prompt_path.read_text(encoding="utf-8")},
        *trim_history(st.session_state.history, 5),
        {"role": "user", "content": user_text},
    ]
    turn = {"turn_index": len(st.session_state.transcript["turns"]) + 1, "started_at": datetime.now().isoformat(timespec="seconds"), "user": user_text}
    try:
        result = run_model_tool_loop(
            provider=make_provider(provider_name),
            messages=messages,
            tools=to_openai_tools(load_tool_declarations(tools_path)),
            model=None,
            max_tool_rounds=4,
        )
        turn.update(result)
        answer, events = result["assistant_text"], result["tool_events"]
        st.session_state.history += [{"role": "user", "content": user_text}, {"role": "assistant", "content": answer}]
    except Exception as exc:
        answer, events = f"ERROR: {type(exc).__name__}: {exc}", []
        turn.update({"status": "provider_error", "error": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
        for event in events:
            with st.expander(f"🔧 {event['tool']}"):
                st.code(json.dumps({"args": event["args"], "result": event["result"]}, ensure_ascii=False, indent=2, default=str)[:4000], language="json")
    st.session_state.display += [("user", user_text, []), ("assistant", answer, events)]
    turn["ended_at"] = datetime.now().isoformat(timespec="seconds")
    st.session_state.transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
