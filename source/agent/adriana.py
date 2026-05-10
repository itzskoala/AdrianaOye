"""
Adriana — intent classifier and action router.

Classifies user messages into intents, fans out to the appropriate
pipeline/store calls, and formats a plain-text reply.
"""

import asyncio
import re
from enum import Enum
from typing import Literal

from source.db.store import store
from source.pipeline.pipeline import Pipeline

Source = Literal["reddit", "instagram", "facebook", "news"]

_pipeline = Pipeline()


class Intent(str, Enum):
    TRENDING  = "trending"
    REDDIT    = "reddit"
    INSTAGRAM = "instagram"
    FACEBOOK  = "facebook"
    NEWS      = "news"
    SENTIMENT = "sentiment"
    ANALYZE   = "analyze"
    UNKNOWN   = "unknown"


_STOP = {
    "what", "is", "are", "the", "on", "about", "saying", "people", "who",
    "how", "can", "you", "find", "show", "me", "tell", "i", "a", "an",
    "reddit", "instagram", "facebook", "news", "right", "now", "any",
    "get", "give", "please", "lately", "recent", "currently",
}

_SOURCE_KEYWORDS: dict[str, Source] = {
    "reddit": "reddit",
    "subreddit": "reddit",
    "instagram": "instagram",
    "ig": "instagram",
    "facebook": "facebook",
    "fb": "facebook",
    "news": "news",
    "article": "news",
    "headlines": "news",
}

_TRENDING_WORDS = {"trend", "trending", "popular", "viral", "hot", "top", "rising"}
_SENTIMENT_WORDS = {"sentiment", "feeling", "feel", "opinion", "think", "attitude"}


def _extract_query(msg: str, remove: str = "") -> str:
    words = re.sub(r"[^\w\s]", "", msg.lower()).split()
    filtered = [w for w in words if w not in _STOP and w != remove]
    return " ".join(filtered).strip() or msg.strip()


def classify(message: str) -> tuple[Intent, Source | None, str]:
    """Returns (intent, source_if_any, query)."""
    low = message.lower()

    detected_source: Source | None = None
    for kw, src in _SOURCE_KEYWORDS.items():
        if kw in low:
            detected_source = src
            break

    if any(w in low for w in _TRENDING_WORDS):
        return Intent.TRENDING, detected_source, _extract_query(low, remove=detected_source or "")
    if any(w in low for w in _SENTIMENT_WORDS):
        return Intent.SENTIMENT, detected_source, _extract_query(low, remove=detected_source or "")
    if detected_source:
        return Intent(detected_source), detected_source, _extract_query(low, remove=detected_source)

    return Intent.ANALYZE, None, _extract_query(low)


# ── Response formatters ────────────────────────────────────────────────────────

def _fmt_pipeline(result, source: str, query: str) -> str:
    if not result.insights:
        return (
            f"I pulled **{result.total_posts}** posts from {source} about '{query}', "
            "but didn't find a strong trend yet. Try a more specific or broader topic."
        )
    top = result.insights[0]
    kws = ", ".join(top.keywords[:3])
    lines = [
        f"Analyzed **{result.total_posts} posts** from {source} about '{query}'.\n",
        f"Top topic: **{kws}**",
        f"{top.summary}\n",
        f"Key insight: {top.key_insight}",
    ]
    if result.trending_count > 1:
        other = [", ".join(i.keywords[:2]) for i in result.insights[1:3]]
        lines.append(f"\nAlso trending: {' · '.join(other)}")
    return "\n".join(lines)


def _fmt_trending(topics: list[dict]) -> str:
    if not topics:
        return (
            "No trending data yet — run an analysis first by asking something like "
            "'What's happening on Reddit about AI?'"
        )
    lines = ["Here's what's trending right now:\n"]
    for i, t in enumerate(topics[:5], 1):
        kws = ", ".join(t.get("keywords", [])[:3])
        eng = t.get("engagement", 0)
        lines.append(f"{i}. **{kws}** — {eng:,} engagements")
    return "\n".join(lines)


# ── Agent ─────────────────────────────────────────────────────────────────────

async def chat(message: str) -> str:
    intent, source, query = classify(message)

    if not query:
        query = "trending"

    try:
        if intent == Intent.TRENDING:
            if source:
                result = await _pipeline.run(source, query or "trending", limit=25)
                return _fmt_pipeline(result, source, query or "trending")
            topics = await store.get_top_trending(5)
            return _fmt_trending(topics)

        if intent == Intent.SENTIMENT:
            target_source: Source = source or "reddit"
            result = await _pipeline.run(target_source, query or "general", limit=25)
            if not result.insights:
                return f"Not enough data to assess sentiment for '{query}' right now."
            top = result.insights[0]
            return (
                f"Sentiment for **{', '.join(top.keywords[:3])}** on {target_source}: "
                f"**{top.sentiment}**.\n\n{top.summary}"
            )

        if intent in (Intent.REDDIT, Intent.INSTAGRAM, Intent.FACEBOOK, Intent.NEWS):
            actual_source: Source = source or "reddit"
            result = await _pipeline.run(actual_source, query, limit=25)
            return _fmt_pipeline(result, actual_source, query)

        if intent == Intent.ANALYZE:
            results = await asyncio.gather(
                _pipeline.run("reddit", query, limit=20),
                _pipeline.run("news",   query, limit=20),
                return_exceptions=True,
            )
            good = [r for r in results if not isinstance(r, Exception) and r.insights]
            if not good:
                return (
                    f"I searched for '{query}' across Reddit and News but couldn't find "
                    "strong signal. Try a more specific term."
                )
            best = max(good, key=lambda r: r.trending_count)
            total = sum(r.total_posts for r in good)
            top = best.insights[0]
            return (
                f"Analyzed **{total} posts** about '{query}' across Reddit & News.\n\n"
                f"Top topic: **{', '.join(top.keywords[:3])}**\n"
                f"{top.summary}\n\n"
                f"Key insight: {top.key_insight}"
            )

    except Exception as exc:
        return f"I hit an error pulling that data: {exc}. Try rephrasing or ask about a specific platform."

    return "I'm not sure how to answer that. Try asking about a specific topic or platform!"
