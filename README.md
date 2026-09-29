# My Assistant — a Claude-style chat on the Gemini API

A minimal chat assistant built with Streamlit and Google's Gemini API.
It keeps conversation history, streams replies, lets you edit the persona
in the sidebar, and lets you download any conversation as markdown.

## How it works

Every AI assistant is the same loop:

1. Keep a list of messages (the history).
2. Send the whole history plus the new message to the model.
3. Append the model's reply to the history.
4. Repeat.

`app.py` is that loop wrapped in a Streamlit UI. `system_prompt.md` is the
persona — edit it to change how the assistant behaves.

## Run locally

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then paste your key in
streamlit run app.py
```

Get a free Gemini API key at https://aistudio.google.com/apikey

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repo (`secrets.toml` is git-ignored, so your key never leaves your machine).
2. Go to https://share.streamlit.io, click **New app**, pick the repo, branch and `app.py`.
3. Open **Advanced settings → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "your-key"
   ```
4. Click **Deploy**.

## Notes

- Streamlit Cloud's disk is wiped on every restart, so conversations are not
  stored server-side. Use the **Download conversation** button to keep one.
- To change the model, edit the `MODEL` constant at the top of `app.py`.
- Next steps if you want to grow it: add tools with Gemini function calling
  (file reading, code execution, web search), or persist chats to a database.
