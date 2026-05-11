"""
Persistent conversation memory using SQLite.
Saves every user message and AI response so the agent has full context
across sessions — even after closing and reopening the browser.
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("MEMORY_DB_PATH", "adriana_memory.db"))


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            role    TEXT NOT NULL,
            content TEXT NOT NULL,
            ts      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def save(role: str, content: str) -> None:
    """Save one message (role = 'user' or 'assistant')."""
    with _conn() as conn:
        conn.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))


def load(limit: int = 60) -> list[dict]:
    """
    Load the most recent `limit` messages in chronological order.
    60 messages = ~30 back-and-forth exchanges, enough context without
    overloading Gemini's context window.
    """
    with _conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM history ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def clear() -> None:
    """Wipe the entire conversation history."""
    with _conn() as conn:
        conn.execute("DELETE FROM history")


def recent_summary(n: int = 10) -> str:
    """Return the last n exchanges as plain text — useful for debugging."""
    messages = load(limit=n * 2)
    lines = []
    for m in messages:
        prefix = "You" if m["role"] == "user" else "Adriana"
        lines.append(f"{prefix}: {m['content'][:200]}")
    return "\n".join(lines) if lines else "No history yet."
