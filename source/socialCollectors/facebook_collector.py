import os
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, computed_field

APIFY_ACTOR = "apify~facebook-posts-scraper"
APIFY_BASE = "https://api.apify.com/v2"
RUN_SYNC_URL = f"{APIFY_BASE}/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"


class FacebookPost(BaseModel):
    url: str | None = None
    text: str | None = None
    likes: int = 0
    comments: int = 0
    shares: int = 0
    timestamp: datetime | None = None
    page_name: str | None = None
    image_url: str | None = None

    @computed_field
    @property
    def engagement_score(self) -> int:
        # Shares carry highest social weight — they extend reach beyond the original audience
        return self.likes + (self.comments * 2) + (self.shares * 3)


class ScrapeResult(BaseModel):
    source: str
    query: str
    posts: list[FacebookPost]
    fetched_at: datetime
    total: int


class FacebookCollector:
    def __init__(self):
        self.token = os.getenv("APIFY_TOKEN")
        if not self.token:
            raise RuntimeError("APIFY_TOKEN is not set in your .env file")

    async def scrape_page(self, page: str, limit: int = 20) -> ScrapeResult:
        """Scrape recent posts from a public Facebook page by name or URL slug."""
        clean = page.lstrip("@").rstrip("/")
        page_url = clean if clean.startswith("http") else f"https://www.facebook.com/{clean}"
        items = await self._run({
            "startUrls": [{"url": page_url}],
            "resultsLimit": limit,
        })
        return ScrapeResult(
            source="page",
            query=clean,
            posts=[self._parse(i) for i in items],
            fetched_at=datetime.now(timezone.utc),
            total=len(items),
        )

    async def _run(self, payload: dict) -> list[dict]:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                RUN_SYNC_URL,
                params={"token": self.token, "timeout": 90},
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    def _parse(self, item: dict) -> FacebookPost:
        return FacebookPost(
            url=item.get("postUrl") or item.get("url"),
            text=item.get("text"),
            likes=item.get("likes", 0),
            comments=item.get("comments", 0),
            shares=item.get("shares", 0),
            timestamp=item.get("time") or item.get("timestamp"),
            page_name=item.get("pageName"),
            image_url=item.get("imageUrl") or item.get("image"),
        )
