import os
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel
from typing import Literal

SERPER_URL = "https://google.serper.dev/news"

SortBy   = Literal["relevancy", "popularity", "publishedAt"]
Category = Literal["business", "entertainment", "general", "health", "science", "sports", "technology"]


class NewsArticle(BaseModel):
    title: str
    description: str | None = None
    url: str
    image_url: str | None = None
    source: str
    author: str | None = None
    published_at: datetime | None = None
    content: str | None = None


class NewsResult(BaseModel):
    query: str
    articles: list[NewsArticle]
    fetched_at: datetime
    total_results: int
    page: int


class NewsCollector:
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY", "")

    async def search(
        self,
        query: str,
        language: str = "en",
        sort_by: SortBy = "publishedAt",
        limit: int = 20,
        page: int = 1,
    ) -> NewsResult:
        data = await self._post({"q": query, "num": min(limit, 20)})
        articles = [self._parse(a) for a in data.get("news", [])]
        return NewsResult(
            query=query,
            articles=articles,
            fetched_at=datetime.now(timezone.utc),
            total_results=len(articles),
            page=page,
        )

    async def headlines(
        self,
        query: str | None = None,
        category: Category = "general",
        country: str = "us",
        limit: int = 20,
    ) -> NewsResult:
        q = query or f"top {category} news today"
        data = await self._post({"q": q, "num": min(limit, 20)})
        articles = [self._parse(a) for a in data.get("news", [])]
        return NewsResult(
            query=q,
            articles=articles,
            fetched_at=datetime.now(timezone.utc),
            total_results=len(articles),
            page=1,
        )

    async def _post(self, payload: dict) -> dict:
        if not self.api_key:
            raise RuntimeError("SERPER_API_KEY is not set in .env")
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                SERPER_URL,
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    def _parse(self, item: dict) -> NewsArticle:
        return NewsArticle(
            title=item.get("title", ""),
            description=item.get("snippet"),
            url=item.get("link", ""),
            image_url=item.get("imageUrl"),
            source=item.get("source", "Unknown"),
            author=None,
            published_at=self._parse_date(item.get("date")),
            content=None,
        )

    def _parse_date(self, date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        for fmt in ["%B %d, %Y", "%b %d, %Y", "%Y-%m-%dT%H:%M:%SZ"]:
            try:
                return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return None
