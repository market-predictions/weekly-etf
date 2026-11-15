"""Check the OpenAI key works and list the chat models it can use."""
from __future__ import annotations

import os

import requests


def main() -> None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("LLM_PROBE no OPENAI_API_KEY")
        return
    r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=30)
    print(f"LLM_PROBE models http={r.status_code}")
    if r.status_code != 200:
        print("LLM_PROBE body:", r.text[:300])
        return
    ids = sorted(m["id"] for m in r.json().get("data", []))
    chat = [i for i in ids if i.startswith(("gpt-", "o")) and not any(x in i for x in ("audio", "realtime", "tts", "transcribe", "image", "search", "embedding"))]
    print("LLM_PROBE chat models:", ", ".join(chat))


if __name__ == "__main__":
    main()
