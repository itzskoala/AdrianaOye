import os

import redis.asyncio as aioredis

_client: aioredis.Redis | None = None

CACHE_TTL    = 300    # pipeline result cache: 5 minutes
RANKING_TTL  = 86400  # trending topic metadata: 24 hours

# Redis key namespaces
def cache_key(source: str, query: str) -> str:
    return f"cache:pipeline:{source}:{query.lower().replace(' ', '_')}"

def topic_meta_key(fingerprint: str) -> str:
    return f"topic:meta:{fingerprint}"

TRENDING_ZSET = "trending:scores"   # sorted set: fingerprint → combined trend score


def get() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True,
        )
    return _client


async def close() -> None:
    global _client
    if _client:
        await _client.aclose()
        _client = None
