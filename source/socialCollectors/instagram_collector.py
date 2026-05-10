import os
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, computed_field

APIFY_ACTOR = "apify~instagram-scraper"
APIFY_BASE = "https://api.apify.com/v2"

# Apify run-sync endpoint: starts the actor, waits, returns dataset items in one call
RUN_SYNC_URL = f"{APIFY_BASE}/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"


class InstagramPost(BaseModel):
    url: str
    caption: str | None = None
    likes: int = 0
    comments: int = 0
    timestamp: datetime | None = None
    username: str | None = None
    hashtags: list[str] = []
    image_url: str | None = None

    @computed_field
    @property
    def engagement_score(self) -> int:
        # Comments = 2x weight — replying takes more intent than a passive like
        return self.likes + (self.comments * 2)


class ScrapeResult(BaseModel):
    source: str          # "hashtag" or "profile"
    query: str
    posts: list[InstagramPost]
    fetched_at: datetime
    total: int


class InstagramCollector:
    def __init__(self):
        self.token = os.getenv("APIFY_TOKEN")
        if not self.token:
            raise RuntimeError("APIFY_TOKEN is not set in your .env file")

    async def scrape_hashtag(self, hashtag: str, limit: int = 20) -> ScrapeResult:
        clean = hashtag.lstrip("#")
        items = await self._run({"hashtags": [clean], "resultsLimit": limit})
        return ScrapeResult(
            source="hashtag",
            query=f"#{clean}",
            posts=[self._parse(i) for i in items],
            fetched_at=datetime.now(timezone.utc),
            total=len(items),
        )

    async def scrape_profile(self, username: str, limit: int = 20) -> ScrapeResult:
        clean = username.lstrip("@")
        items = await self._run({"usernames": [clean], "resultsLimit": limit})
        return ScrapeResult(
            source="profile",
            query=f"@{clean}",
            posts=[self._parse(i) for i in items],
            fetched_at=datetime.now(timezone.utc),
            total=len(items),
        )

    async def _run(self, payload: dict) -> list[dict]:
        # timeout=90s for Apify to finish the scrape + 30s for our HTTP layer
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                RUN_SYNC_URL,
                params={"token": self.token, "timeout": 90},
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    def _parse(self, item: dict) -> InstagramPost:
        return InstagramPost(
            url=item.get("url", ""),
            caption=item.get("caption"),
            likes=item.get("likesCount", 0),
            comments=item.get("commentsCount", 0),
            timestamp=item.get("timestamp"),
            username=item.get("ownerUsername"),
            hashtags=item.get("hashtags", []),
            image_url=item.get("displayUrl"),
        )
