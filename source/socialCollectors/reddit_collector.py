from datetime import datetime, timezone
from typing import Literal

import httpx
from pydantic import BaseModel, computed_field

REDDIT_BASE = "https://www.reddit.com"
# Reddit blocks requests without a User-Agent — this identifies our bot
HEADERS = {"User-Agent": "SocialListeningBot/1.0"}

Sort = Literal["new", "hot", "top", "rising", "controversial"]


class RedditPost(BaseModel):
    title: str
    body: str | None = None
    url: str
    permalink: str
    subreddit: str
    author: str | None = None
    upvotes: int = 0
    upvote_ratio: float = 0.0
    num_comments: int = 0
    flair: str | None = None
    created_at: datetime | None = None
    is_self: bool = True        # True = text post, False = link post

    @computed_field
    @property
    def engagement_score(self) -> int:
        # Upvotes reflect reach; comments reflect conversation depth
        return self.upvotes + (self.num_comments * 3)


class RedditResult(BaseModel):
    source: str          # "subreddit" or "search"
    query: str
    posts: list[RedditPost]
    fetched_at: datetime
    total: int


class RedditCollector:
    async def search(
        self,
        query: str,
        sort: Sort = "new",
        limit: int = 25,
    ) -> RedditResult:
        """Search across all of Reddit for a keyword or phrase."""
        data = await self._get("/search.json", {"q": query, "sort": sort, "limit": limit})
        posts = [self._parse(c["data"]) for c in data["data"]["children"] if c["kind"] == "t3"]
        return RedditResult(
            source="search",
            query=query,
            posts=posts,
            fetched_at=datetime.now(timezone.utc),
            total=len(posts),
        )

    async def subreddit(
        self,
        name: str,
        sort: Sort = "hot",
        limit: int = 25,
    ) -> RedditResult:
        """Get posts from a specific subreddit."""
        clean = name.lstrip("r/").lstrip("/")
        data = await self._get(f"/r/{clean}/{sort}.json", {"limit": limit})
        posts = [self._parse(c["data"]) for c in data["data"]["children"] if c["kind"] == "t3"]
        return RedditResult(
            source="subreddit",
            query=f"r/{clean}",
            posts=posts,
            fetched_at=datetime.now(timezone.utc),
            total=len(posts),
        )

    async def _get(self, path: str, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            resp = await client.get(f"{REDDIT_BASE}{path}", params=params)
            resp.raise_for_status()
            return resp.json()

    def _parse(self, d: dict) -> RedditPost:
        created = d.get("created_utc")
        return RedditPost(
            title=d.get("title", ""),
            body=d.get("selftext") or None,
            url=d.get("url", ""),
            permalink=f"https://www.reddit.com{d.get('permalink', '')}",
            subreddit=d.get("subreddit", ""),
            author=d.get("author"),
            upvotes=d.get("score", 0),
            upvote_ratio=d.get("upvote_ratio", 0.0),
            num_comments=d.get("num_comments", 0),
            flair=d.get("link_flair_text"),
            created_at=datetime.fromtimestamp(created, tz=timezone.utc) if created else None,
            is_self=d.get("is_self", True),
        )
