"""
Adriana — agent logic shared by the Gradio UI (app.py) and the FastAPI chat endpoint (api/chat.py).
"""

import asyncio
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

from source.agent.formatter import format_response

load_dotenv(override=True)

API          = "http://localhost:8000"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# ── Tool functions ─────────────────────────────────────────────────────────────

def search_reddit(query: str, limit: int = 15) -> dict:
    try:
        r = requests.get(f"{API}/reddit/search", params={"q": query, "limit": min(limit, 25)}, timeout=20)
        posts = r.json().get("posts", [])
        return {
            "total": len(posts),
            "posts": [{"title": p.get("title"), "body": (p.get("body") or "")[:300],
                        "subreddit": p.get("subreddit"), "upvotes": p.get("upvotes"),
                        "num_comments": p.get("num_comments"), "engagement": p.get("engagement_score"),
                        "url": p.get("url")} for p in posts],
        }
    except Exception as e:
        return {"error": str(e)}


def get_subreddit(subreddit: str, sort: str = "hot", limit: int = 15) -> dict:
    try:
        r = requests.get(f"{API}/reddit/r/{subreddit}", params={"sort": sort, "limit": min(limit, 25)}, timeout=20)
        posts = r.json().get("posts", [])
        return {
            "subreddit": subreddit, "total": len(posts),
            "posts": [{"title": p.get("title"), "upvotes": p.get("upvotes"),
                        "num_comments": p.get("num_comments"), "engagement": p.get("engagement_score"),
                        "url": p.get("url")} for p in posts],
        }
    except Exception as e:
        return {"error": str(e)}


def search_news(query: str, limit: int = 10) -> dict:
    try:
        r = requests.get(f"{API}/news/search", params={"q": query, "limit": min(limit, 20)}, timeout=20)
        articles = r.json().get("articles", [])
        return {
            "total": len(articles),
            "articles": [{"title": a.get("title"), "source": a.get("source"),
                           "description": (a.get("description") or "")[:300],
                           "published_at": a.get("published_at"), "url": a.get("url")} for a in articles],
        }
    except Exception as e:
        return {"error": str(e)}


def search_web(query: str, limit: int = 8) -> dict:
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return {"error": "SERPER_API_KEY not set in .env"}
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"q": query, "num": min(limit, 10)},
            timeout=15,
        )
        data = r.json()
        results = []
        if "answerBox" in data:
            box = data["answerBox"]
            results.append({"type": "answer_box", "title": box.get("title"),
                             "answer": box.get("answer") or box.get("snippet", "")[:300]})
        for item in data.get("organic", [])[:limit]:
            results.append({"type": "organic", "title": item.get("title"),
                             "snippet": item.get("snippet", "")[:300], "url": item.get("link")})
        return {"total": len(results), "results": results}
    except Exception as e:
        return {"error": str(e)}


def get_trending_topics(limit: int = 8) -> dict:
    try:
        r = requests.get(f"{API}/pipeline/trending", params={"limit": limit}, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_instagram_hashtag(hashtag: str, limit: int = 20) -> dict:
    try:
        tag = hashtag.lstrip("#")
        r = requests.get(f"{API}/instagram/hashtag/{tag}", params={"limit": min(limit, 50)}, timeout=60)
        posts = r.json().get("posts", [])
        return {
            "hashtag": f"#{tag}", "total": len(posts),
            "posts": [{"caption": (p.get("caption") or "")[:300], "likes": p.get("likes"),
                        "comments": p.get("comments"), "username": p.get("username"),
                        "engagement": p.get("engagement_score")} for p in posts],
        }
    except Exception as e:
        return {"error": str(e)}


def get_instagram_profile(username: str) -> dict:
    try:
        r = requests.get(f"{API}/instagram/profile/{username}", timeout=60)
        posts = r.json().get("posts", [])
        return {
            "username": username, "total": len(posts),
            "posts": [{"caption": (p.get("caption") or "")[:300], "likes": p.get("likes"),
                        "comments": p.get("comments"), "engagement": p.get("engagement_score")} for p in posts],
        }
    except Exception as e:
        return {"error": str(e)}


def get_facebook_page(page: str, limit: int = 20) -> dict:
    try:
        r = requests.get(f"{API}/facebook/page/{page}", params={"limit": min(limit, 50)}, timeout=60)
        posts = r.json().get("posts", [])
        return {
            "page": page, "total": len(posts),
            "posts": [{"text": (p.get("text") or "")[:300], "likes": p.get("likes"),
                        "comments": p.get("comments"), "shares": p.get("shares"),
                        "engagement": p.get("engagement_score")} for p in posts],
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_topic(source: str, topic: str, limit: int = 25) -> dict:
    try:
        r = requests.post(
            f"{API}/pipeline/analyze",
            json={"source": source, "query": topic, "limit": min(limit, 50)},
            timeout=120,
        )
        data = r.json()
        return {
            "source": source, "topic": topic,
            "total_posts": data.get("total_posts"),
            "topics_found": data.get("topics_found"),
            "trending_count": data.get("trending_count"),
            "insights": [{"keywords": i.get("keywords", [])[:5], "summary": i.get("summary"),
                           "sentiment": i.get("sentiment"), "key_insight": i.get("key_insight")}
                         for i in data.get("insights", [])[:3]],
        }
    except Exception as e:
        return {"error": str(e)}


def send_email(to_email: str, subject: str, body: str) -> dict:
    sender   = os.getenv("EMAIL_FROM")
    password = os.getenv("EMAIL_APP_PASSWORD")
    if not sender or not password:
        return {"error": "EMAIL_FROM and EMAIL_APP_PASSWORD must be set in .env"}
    try:
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = sender, to_email, subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(sender, password)
            s.send_message(msg)
        return {"sent": True, "to": to_email}
    except Exception as e:
        return {"error": str(e)}


TOOL_MAP = {
    "search_reddit":         search_reddit,
    "get_subreddit":         get_subreddit,
    "search_news":           search_news,
    "search_web":            search_web,
    "get_trending_topics":   get_trending_topics,
    "get_instagram_hashtag": get_instagram_hashtag,
    "get_instagram_profile": get_instagram_profile,
    "get_facebook_page":     get_facebook_page,
    "analyze_topic":         analyze_topic,
    "send_email":            send_email,
}


# ── Tool schemas (google-genai types format) ──────────────────────────────────

def _fd(name, description, props, required=None):
    properties = {
        k: types.Schema(type=v["type"].upper(), description=v.get("description", ""))
        for k, v in props.items()
    }
    return types.FunctionDeclaration(
        name=name,
        description=description,
        parameters=types.Schema(
            type="OBJECT",
            properties=properties,
            required=required or [],
        ),
    )

GEMINI_TOOLS = types.Tool(function_declarations=[
    _fd("search_reddit", "Search Reddit for posts and discussions about any topic.",
        {"query": {"type": "string", "description": "Keywords or topic to search for"},
         "limit": {"type": "integer", "description": "Number of posts, default 15"}},
        ["query"]),
    _fd("get_subreddit", "Get recent posts from a specific subreddit.",
        {"subreddit": {"type": "string", "description": "Subreddit name without r/"},
         "sort": {"type": "string", "description": "hot, new, top, rising, or controversial"},
         "limit": {"type": "integer", "description": "Number of posts, default 15"}},
        ["subreddit"]),
    _fd("search_news", "Search Google News for recent articles about a topic.",
        {"query": {"type": "string", "description": "Topic or keywords"},
         "limit": {"type": "integer", "description": "Number of articles, default 10"}},
        ["query"]),
    _fd("search_web", "Search the open web via Google. Use for general questions, market data, company info, statistics.",
        {"query": {"type": "string", "description": "Search query"},
         "limit": {"type": "integer", "description": "Number of results, default 8"}},
        ["query"]),
    _fd("get_trending_topics", "Get topics currently trending across all monitored platforms.",
        {"limit": {"type": "integer", "description": "Number of topics, default 8"}}),
    _fd("get_instagram_hashtag", "Get recent Instagram posts for a hashtag.",
        {"hashtag": {"type": "string", "description": "Hashtag with or without # (e.g. travel)"},
         "limit": {"type": "integer", "description": "Number of posts, default 20"}},
        ["hashtag"]),
    _fd("get_instagram_profile", "Get recent posts from a public Instagram profile.",
        {"username": {"type": "string", "description": "Instagram username without @"}},
        ["username"]),
    _fd("get_facebook_page", "Get recent posts from a public Facebook page.",
        {"page": {"type": "string", "description": "Facebook page name e.g. nasa or telemundo"},
         "limit": {"type": "integer", "description": "Number of posts, default 20"}},
        ["page"]),
    _fd("analyze_topic",
        ("Run a deep analysis on a topic: fetches posts, runs topic modeling, scores trends, generates insights. "
         "Takes 15-60 seconds. source must be one of: reddit, instagram, facebook, news"),
        {"source": {"type": "string", "description": "Platform: reddit, instagram, facebook, or news"},
         "topic": {"type": "string", "description": "Topic to analyze"},
         "limit": {"type": "integer", "description": "Number of posts, default 25"}},
        ["source", "topic"]),
    _fd("send_email", "Send an email report to a stakeholder.",
        {"to_email": {"type": "string", "description": "Recipient email address"},
         "subject": {"type": "string", "description": "Subject line"},
         "body": {"type": "string", "description": "Full email body"}},
        ["to_email", "subject", "body"]),
])


SYSTEM_PROMPT = (
    "You are Adriana, a social intelligence analyst. "
    "You help users understand what people are saying across Reddit, Instagram, Facebook, and the news in real time.\n\n"

    "## Tools available\n"
    "- search_reddit: Full-text search across all of Reddit. Best for 'what are people saying about X'.\n"
    "- get_subreddit: Browse a specific subreddit (e.g. r/technology, r/stocks).\n"
    "- search_news: Search Google News for recent articles.\n"
    "- search_web: Google search for facts, statistics, market data, current events.\n"
    "- get_trending_topics: What is trending right now across monitored platforms.\n"
    "- get_instagram_hashtag: Posts that use a specific hashtag. Good for lifestyle/trend tags like #travel or #fitness. NOT useful for brand names — few people hashtag brand names.\n"
    "- get_instagram_profile: Recent posts FROM a specific Instagram account. Use this when the user asks what a brand or person is posting on Instagram.\n"
    "- get_facebook_page: Recent posts FROM a public Facebook page. Use this when the user asks what a brand or page is posting on Facebook.\n"
    "- analyze_topic: Deep BERTopic analysis on a platform. Slow (15-60s) — only use when the user explicitly asks for deep or detailed analysis.\n"
    "- send_email: Send an email report. Use when the user asks to email findings.\n\n"

    "## Tool routing rules\n"
    "- 'What are people saying about X?' → search_reddit(X) + search_news(X). Reddit is where public opinion lives.\n"
    "- 'What is [Brand] posting on Instagram?' → get_instagram_profile(brand_username)\n"
    "- 'What are people posting about #[hashtag] on Instagram?' → get_instagram_hashtag(hashtag)\n"
    "- 'What is [Brand] posting on Facebook?' → get_facebook_page(page_name)\n"
    "- 'What's trending?' → get_trending_topics()\n"
    "- 'Latest news on X?' → search_news(X)\n"
    "- For any factual question (price, stats, market data) → search_web()\n"
    "- Never use get_instagram_hashtag for brand name queries — use get_instagram_profile instead.\n\n"

    "## Behavior rules\n"
    "- CRITICAL: Never say 'I will search' or 'I need to look this up' or describe what you are about to do. Just call the tool immediately — no announcements.\n"
    "- CRITICAL: If a first search returns weak results, call another tool (try different query or different platform) before giving up. Do not stop and explain why results were bad.\n"
    "- Always call at least one tool before answering any question about current events, trends, or social media.\n"
    "- Be specific: cite post counts, upvotes, engagement scores, and sentiment when you have them.\n"
    "- Keep answers concise and data-driven. Lead with the data, then the insight.\n"
    "- Always include source links at the end of your answer. For Reddit posts include the post URL. "
    "For news articles include the article URL. For web results include the page URL. "
    "Format them as a short 'Sources:' list using markdown links."
)


_CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[GEMINI_TOOLS],
)


class Adriana:
    def run(self, message: str, history: list = []) -> str:
        """Sync entry point — used by Gradio and (via asyncio.to_thread) by FastAPI."""
        contents = []
        for h in history:
            role    = h.get("role")
            content = h.get("content")
            if role == "user" and isinstance(content, str):
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=content)]))
            elif role == "assistant" and isinstance(content, str):
                contents.append(types.Content(role="model", parts=[types.Part.from_text(text=content)]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))

        try:
            response = _client.models.generate_content(
                model=GEMINI_MODEL, contents=contents, config=_CONFIG
            )
        except Exception as e:
            return f"Could not reach Gemini: {e}\n\nMake sure GOOGLE_API_KEY is set in .env"

        while True:
            fn_calls = [p.function_call for p in (response.candidates[0].content.parts or [])
                        if p.function_call and p.function_call.name]

            if not fn_calls:
                raw = response.text or "I couldn't generate a response."
                return format_response(raw)

            # Append model turn (with function calls)
            contents.append(response.candidates[0].content)

            # Execute tools and build response turn
            fn_parts = []
            for fc in fn_calls:
                name   = fc.name
                args   = dict(fc.args)
                print(f"[tool] {name}({args})", flush=True)
                fn     = TOOL_MAP.get(name)
                result = fn(**args) if fn else {"error": f"Unknown tool: {name}"}
                fn_parts.append(
                    types.Part.from_function_response(name=name, response={"result": json.dumps(result)})
                )

            contents.append(types.Content(role="user", parts=fn_parts))

            try:
                response = _client.models.generate_content(
                    model=GEMINI_MODEL, contents=contents, config=_CONFIG
                )
            except Exception as e:
                return format_response(f"Error after tool call: {e}")


# Module-level instance shared by both entry points
_agent = Adriana()


def chat_sync(message: str, history: list) -> str:
    """For Gradio (synchronous)."""
    return _agent.run(message, history)


async def chat(message: str) -> str:
    """For FastAPI (async) — runs the sync agent in a thread pool."""
    return await asyncio.to_thread(_agent.run, message)
