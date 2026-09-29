"""
My own Claude-style chat, powered by the Gemini API.

The whole idea is one loop:
    1. keep a list of messages (the conversation history)
    2. send the history + the new user message to the model
    3. stream the reply back and append it to the history
Everything else is just UI.
"""

import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

# ---------- configuration ----------

MODEL = "gemini-2.5-flash"           # change to gemini-2.5-pro for stronger (slower, pricier) answers
PROMPT_FILE = Path(__file__).parent / "system_prompt.md"


def get_api_key() -> str | None:
    """Streamlit Cloud -> st.secrets; local -> environment variable."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.getenv("GEMINI_API_KEY")


def load_system_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    return "You are a helpful assistant."


# ---------- page setup ----------

st.set_page_config(page_title="My Assistant", page_icon="💬")
st.title("My Assistant")

api_key = get_api_key()
if not api_key:
    st.error("No GEMINI_API_KEY found. Add it to .streamlit/secrets.toml or set it as an environment variable.")
    st.stop()

client = genai.Client(api_key=api_key)

# ---------- sidebar ----------

with st.sidebar:
    st.subheader("Settings")
    system_prompt = st.text_area(
        "System prompt (persona / instructions)",
        value=load_system_prompt(),
        height=250,
    )
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)

    if st.button("New conversation"):
        st.session_state.messages = []
        st.rerun()

    # Streamlit Cloud's disk is wiped on every restart, so "saving" a log
    # means letting the user download it, not writing to a file.
    if st.session_state.get("messages"):
        transcript = "\n\n".join(
            f"**{m['role'].title()}:** {m['content']}" for m in st.session_state.messages
        )
        st.download_button(
            "Download conversation",
            data=transcript,
            file_name=f"chat_{datetime.now():%Y%m%d_%H%M}.md",
            mime="text/markdown",
        )

# ---------- conversation state ----------

if "messages" not in st.session_state:
    st.session_state.messages = []      # each item: {"role": "user"|"assistant", "content": str}

# replay the history so it stays on screen across reruns
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------- the loop ----------

if user_text := st.chat_input("Ask me anything"):
    # 1. show + store the user's message
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # 2. convert our history into Gemini's format (Gemini calls the assistant "model")
    history = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in st.session_state.messages
    ]

    # 3. call the model and stream the answer
    with st.chat_message("assistant"):
        try:
            stream = client.models.generate_content_stream(
                model=MODEL,
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                ),
            )
            reply = st.write_stream(chunk.text or "" for chunk in stream)
        except Exception as e:  # noqa: BLE001
            reply = f"Something went wrong: {e}"
            st.error(reply)

    # 4. store the reply so the next turn has full context
    st.session_state.messages.append({"role": "assistant", "content": reply})
