"""
Formatter agent — takes Adriana's raw analyst output and makes it clean,
presentable, motivational, and inspiring. Uses Ollama locally since this
is pure text transformation (no tool calls needed, so the smaller model works fine).
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv(override=True)

OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

FORMATTER_SYSTEM = """\
You are a presentation specialist for a social intelligence platform called Adriana.
Your job is to take raw analyst output and reformat it into a beautifully formatted, motivational, and inspiring report.

Rules:
- NEVER change, remove, invent, or alter any facts, numbers, names, or links — preserve them 100%
- Use markdown: ## for main sections, ### for sub-sections, **bold** for key numbers and takeaways
- Add relevant emojis at the start of each section header to make it visually engaging, but not too many
- Frame insights with energy and forward momentum ("The data reveals...", "Here's what's capturing attention...", "The conversation is buzzing about...")
- End every response with a short ## ✨ Key Takeaway section — one punchy sentence that summarizes the most important insight
- Keep it concise. No filler words, no padding. Every sentence must earn its place.
- If there are source links, preserve them in a ## 🔗 Sources section at the very end
- Never add fake data or speculate beyond what the raw input contains
"""


def format_response(raw: str) -> str:
    """
    Sends Adriana's raw output to Ollama for motivational formatting.
    Falls back to the original text if Ollama is unreachable.
    """
    if not raw or not raw.strip():
        return raw

    messages = [
        {"role": "system", "content": FORMATTER_SYSTEM},
        {"role": "user", "content": f"Format this analyst output:\n\n{raw}"},
    ]

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            timeout=60,
        )
        r.raise_for_status()
        content = r.json().get("message", {}).get("content", "").strip()
        return content if content else raw
    except Exception:
        return raw
