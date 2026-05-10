import json
from datetime import datetime, timezone

from source.db import postgres, redis_client
from source.pipeline.models import PipelineResult, Post, TopicInsight, TrendScore


def _fingerprint(keywords: list[str]) -> str:
    """Stable identity for a topic — top 3 keywords sorted so order doesn't matter."""
    return ":".join(sorted(k.lower() for k in keywords[:3]))


def _trend_score(velocity: float, spike: float) -> float:
    """Single combined ranking score for Redis sorted set."""
    return round(velocity * 0.6 + spike * 0.4, 4)


class Store:
    # ── Cache ─────────────────────────────────────────────────────────────────

    async def get_cached_result(self, source: str, query: str) -> PipelineResult | None:
        r = redis_client.get()
        raw = await r.get(redis_client.cache_key(source, query))
        if raw:
            return PipelineResult.model_validate_json(raw)
        return None

    async def cache_result(self, result: PipelineResult) -> None:
        r = redis_client.get()
        await r.setex(
            redis_client.cache_key(result.source, result.query),
            redis_client.CACHE_TTL,
            result.model_dump_json(),
        )

    # ── Posts ─────────────────────────────────────────────────────────────────

    async def save_posts(self, posts: list[Post]) -> None:
        """Upsert posts — ON CONFLICT DO NOTHING deduplicates by URL."""
        rows = [
            (p.source, p.url, p.text, p.engagement, p.timestamp)
            for p in posts
            if p.url  # skip posts with no URL — can't deduplicate them
        ]
        if not rows:
            return
        db = postgres.pool()
        async with db.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO posts (source, url, text, engagement, post_ts)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (url) DO NOTHING
                """,
                rows,
            )

    # ── Topics ────────────────────────────────────────────────────────────────

    async def upsert_topic(self, keywords: list[str]) -> str:
        """
        Insert a topic or update last_seen if it already exists.
        Returns the fingerprint (primary key).
        """
        fp = _fingerprint(keywords)
        db = postgres.pool()
        async with db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO topics (fingerprint, keywords)
                VALUES ($1, $2)
                ON CONFLICT (fingerprint) DO UPDATE SET
                    last_seen = NOW(),
                    keywords  = EXCLUDED.keywords
                """,
                fp,
                keywords,
            )
        return fp

    # ── Trend Snapshots ───────────────────────────────────────────────────────

    async def save_trend_snapshot(
        self,
        trend: TrendScore,
        source: str,
        query: str,
        post_count: int,
    ) -> None:
        fp = await self.upsert_topic(trend.keywords)
        db = postgres.pool()
        async with db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO trend_snapshots
                    (topic_fingerprint, source, query, velocity, spike,
                     total_engagement, post_count, is_trending)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                fp, source, query,
                trend.velocity, trend.spike,
                trend.total_engagement, post_count, trend.is_trending,
            )

        # Mirror to Redis for fast ranking queries
        if trend.is_trending:
            await self._update_ranking(fp, trend)

    async def _update_ranking(self, fingerprint: str, trend: TrendScore) -> None:
        r = redis_client.get()
        score = _trend_score(trend.velocity, trend.spike)

        # Sorted set: fingerprint scored by combined trend signal
        await r.zadd(redis_client.TRENDING_ZSET, {fingerprint: score})

        # Store metadata alongside so we can return it without a Postgres query
        await r.hset(
            redis_client.topic_meta_key(fingerprint),
            mapping={
                "keywords":    json.dumps(trend.keywords),
                "velocity":    trend.velocity,
                "spike":       trend.spike,
                "engagement":  trend.total_engagement,
                "score":       score,
            },
        )
        await r.expire(redis_client.topic_meta_key(fingerprint), redis_client.RANKING_TTL)

    # ── Insights ──────────────────────────────────────────────────────────────

    async def save_insight(self, insight: TopicInsight) -> None:
        fp = _fingerprint(insight.keywords)
        db = postgres.pool()
        async with db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO insights (topic_fingerprint, summary, sentiment, key_insight)
                VALUES ($1, $2, $3, $4)
                """,
                fp, insight.summary, insight.sentiment, insight.key_insight,
            )

    # ── Queries ───────────────────────────────────────────────────────────────

    async def get_top_trending(self, limit: int = 10) -> list[dict]:
        """
        Read the top N trending topics from Redis — microsecond reads, no Postgres hit.
        Returns highest-scored topics first.
        """
        r = redis_client.get()
        # ZREVRANGE: highest score first
        entries = await r.zrevrange(redis_client.TRENDING_ZSET, 0, limit - 1, withscores=True)
        results = []
        for fingerprint, score in entries:
            meta = await r.hgetall(redis_client.topic_meta_key(fingerprint))
            if meta:
                results.append({
                    "fingerprint": fingerprint,
                    "keywords":    json.loads(meta["keywords"]),
                    "velocity":    float(meta["velocity"]),
                    "spike":       float(meta["spike"]),
                    "engagement":  int(meta["engagement"]),
                    "score":       score,
                })
        return results

    async def get_topic_history(self, fingerprint: str, limit: int = 30) -> list[dict]:
        """Pull the last N trend snapshots for a topic from Postgres."""
        db = postgres.pool()
        async with db.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT velocity, spike, total_engagement, post_count,
                       is_trending, source, query, snapshot_at
                FROM   trend_snapshots
                WHERE  topic_fingerprint = $1
                ORDER  BY snapshot_at DESC
                LIMIT  $2
                """,
                fingerprint, limit,
            )
        return [dict(r) for r in rows]


store = Store()
