import os
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, computed_field

APIFY_BASE = "https://api.apify.com/v2"

# Two separate actors — each one is purpose-built and actually works
_HASHTAG_ACTOR  = "apify~instagram-hashtag-scraper"
_PROFILE_ACTOR  = "apify~instagram-profile-scraper"

_HASHTAG_URL = f"{APIFY_BASE}/acts/{_HASHTAG_ACTOR}/run-sync-get-dataset-items"
_PROFILE_URL = f"{APIFY_BASE}/acts/{_PROFILE_ACTOR}/run-sync-get-dataset-items"


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
        return self.likes + (self.comments * 2)


class InstagramProfile(BaseModel):
    username: str
    full_name: str | None = None
    biography: str | None = None
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    verified: bool = False
    url: str | None = None


class ScrapeResult(BaseModel):
    source: str          # "hashtag" or "profile"
    query: str
    profile: InstagramProfile | None = None
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
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                _HASHTAG_URL,
                params={"token": self.token, "timeout": 90},
                json={"hashtags": [clean], "resultsLimit": limit},
            )
            resp.raise_for_status()
            items = resp.json()

        posts = [self._parse_post(i) for i in items if isinstance(i, dict) and "url" in i]
        return ScrapeResult(
            source="hashtag",
            query=f"#{clean}",
            posts=posts,
            fetched_at=datetime.now(timezone.utc),
            total=len(posts),
        )

    async def scrape_profile(self, username: str, limit: int = 20) -> ScrapeResult:
        clean = username.lstrip("@")
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                _PROFILE_URL,
                params={"token": self.token, "timeout": 90},
                json={"usernames": [clean]},
            )
            resp.raise_for_status()
            data = resp.json()

        if not data or not isinstance(data, list):
            return ScrapeResult(source="profile", query=f"@{clean}",
                                posts=[], fetched_at=datetime.now(timezone.utc), total=0)

        profile_data = data[0]
        profile = InstagramProfile(
            username=profile_data.get("username", clean),
            full_name=profile_data.get("fullName"),
            biography=profile_data.get("biography"),
            followers=profile_data.get("followersCount", 0),
            following=profile_data.get("followsCount", 0),
            posts_count=profile_data.get("postsCount", 0),
            verified=profile_data.get("verified", False),
            url=profile_data.get("url"),
        )

        raw_posts = profile_data.get("latestPosts", [])[:limit]
        posts = [self._parse_post(p) for p in raw_posts if isinstance(p, dict)]

        return ScrapeResult(
            source="profile",
            query=f"@{clean}",
            profile=profile,
            posts=posts,
            fetched_at=datetime.now(timezone.utc),
            total=len(posts),
        )

    def _parse_post(self, item: dict) -> InstagramPost:
        raw_hashtags = item.get("hashtags", [])
        hashtags = raw_hashtags if isinstance(raw_hashtags, list) else []

        return InstagramPost(
            url=item.get("url", ""),
            caption=item.get("caption"),
            likes=max(0, self._to_int(item.get("likesCount"))),
            comments=max(0, self._to_int(item.get("commentsCount"))),
            timestamp=self._parse_ts(item.get("timestamp")),
            username=item.get("ownerUsername"),
            hashtags=hashtags,
            image_url=item.get("displayUrl"),
        )

    def _to_int(self, val) -> int:
        try:
            return int(val or 0)
        except (ValueError, TypeError):
            return 0

    def _parse_ts(self, ts) -> datetime | None:
        if not ts:
            return None
        try:
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:
            return None
