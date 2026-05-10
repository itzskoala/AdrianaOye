import os
from datetime import datetime, timezone
from typing import Literal

import httpx
from pydantic import BaseModel

NEWS_API_BASE = "https://newsapi.org/v2"

# NewsAPI's accepted values for these params — Literal lets FastAPI validate them for free
SortBy = Literal["relevancy", "popularity", "publishedAt"]
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
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise RuntimeError("NEWS_API_KEY is not set in your .env file")

    async def search(
        self,
        query: str,
        language: str = "en",
        sort_by: SortBy = "publishedAt",
        limit: int = 20,
        page: int = 1,
    ) -> NewsResult:
        """/everything — searches the full article archive across all sources."""
        data = await self._get("/everything", {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": limit,
            "page": page,
        })
        return NewsResult(
            query=query,
            articles=[self._parse(a) for a in data.get("articles", [])],
            fetched_at=datetime.now(timezone.utc),
            total_results=data.get("totalResults", 0),
            page=page,
        )

    async def headlines(
        self,
        query: str | None = None,
        category: Category = "general",
        country: str = "us",
        limit: int = 20,
    ) -> NewsResult:
        """/top-headlines — breaking news filtered by category and country."""
        params: dict = {"category": category, "country": country, "pageSize": limit}
        if query:
            params["q"] = query
        data = await self._get("/top-headlines", params)
        return NewsResult(
            query=query or f"{category} headlines ({country})",
            articles=[self._parse(a) for a in data.get("articles", [])],
            fetched_at=datetime.now(timezone.utc),
            total_results=data.get("totalResults", 0),
            page=1,
        )

    async def _get(self, path: str, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{NEWS_API_BASE}{path}",
                params={**params, "apiKey": self.api_key},
            )
            resp.raise_for_status()
            data = resp.json()
            # NewsAPI returns 200 even on errors — check the status field
            if data.get("status") != "ok":
                raise RuntimeError(data.get("message", "NewsAPI returned an error"))
            return data

    def _parse(self, item: dict) -> NewsArticle:
        return NewsArticle(
            title=item.get("title", ""),
            description=item.get("description"),
            url=item.get("url", ""),
            image_url=item.get("urlToImage"),
            source=item.get("source", {}).get("name", "Unknown"),
            author=item.get("author"),
            published_at=item.get("publishedAt"),
            content=item.get("content"),
        )
