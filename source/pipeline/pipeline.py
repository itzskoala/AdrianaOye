from datetime import datetime, timezone
from typing import Literal

from source.db.store import store
from source.pipeline.insights import InsightsEngine
from source.pipeline.models import Post, PipelineResult
from source.pipeline.topic_model import TopicModeler
from source.pipeline.trend_detector import TrendDetector

# Collectors
from source.socialCollectors.instagram_collector import InstagramCollector
from source.socialCollectors.facebook_collector import FacebookCollector
from source.socialCollectors.reddit_collector import RedditCollector
from source.socialCollectors.news_collector import NewsCollector

Source = Literal["reddit", "instagram", "facebook", "news"]


class Pipeline:
    def __init__(self):
        self.topic_modeler  = TopicModeler()
        self.trend_detector = TrendDetector()
        self.insights       = InsightsEngine()

        self._collectors = {
            "instagram": InstagramCollector(),
            "facebook":  FacebookCollector(),
            "reddit":    RedditCollector(),
            "news":      NewsCollector(),
        }

    async def run(self, source: Source, query: str, limit: int = 50) -> PipelineResult:
        # 0. Return cached result if a fresh run already happened recently
        cached = await store.get_cached_result(source, query)
        if cached:
            return cached

        # 1. Fetch
        posts = await self._fetch(source, query, limit)

        # 2. Topic modeling
        topics, doc_topic_ids = await self.topic_modeler.fit(posts)

        # 3. Trend scoring
        trends = self.trend_detector.score(posts, topics, doc_topic_ids)

        # 4. AI insights (trending topics only)
        insights = await self.insights.analyze(posts, topics, trends, doc_topic_ids)

        result = PipelineResult(
            source=source,
            query=query,
            total_posts=len(posts),
            topics_found=len(topics),
            trending_count=len([t for t in trends if t.is_trending]),
            insights=insights,
            processed_at=datetime.now(timezone.utc),
        )

        # 5. Persist everything
        topic_post_counts = {t.id: sum(1 for tid in doc_topic_ids if tid == t.id) for t in topics}
        await store.save_posts(posts)
        for trend in trends:
            topic = next((t for t in topics if t.id == trend.topic_id), None)
            if topic:
                await store.save_trend_snapshot(trend, source, query, topic_post_counts[topic.id])
        for insight in insights:
            await store.save_insight(insight)

        # 6. Cache the result so repeat calls are instant
        await store.cache_result(result)

        return result

    async def _fetch(self, source: Source, query: str, limit: int) -> list[Post]:
        """Call the right collector and normalize to the unified Post model."""
        c = self._collectors[source]

        if source == "reddit":
            result = await c.search(query, sort="new", limit=limit)
            return [
                Post(
                    text=f"{p.title}. {p.body or ''}".strip(),
                    timestamp=p.created_at,
                    engagement=p.engagement_score,
                    source="reddit",
                    url=p.permalink,
                )
                for p in result.posts
            ]

        if source == "news":
            result = await c.search(query, limit=limit)
            return [
                Post(
                    text=f"{a.title}. {a.description or ''}".strip(),
                    timestamp=a.published_at,
                    engagement=0,
                    source="news",
                    url=a.url,
                )
                for a in result.articles
            ]

        if source == "instagram":
            result = await c.scrape_hashtag(query, limit=limit)
            return [
                Post(
                    text=p.caption or "",
                    timestamp=p.timestamp,
                    engagement=p.engagement_score,
                    source="instagram",
                    url=p.url,
                )
                for p in result.posts if p.caption
            ]

        if source == "facebook":
            result = await c.scrape_page(query, limit=limit)
            return [
                Post(
                    text=p.text or "",
                    timestamp=p.timestamp,
                    engagement=p.engagement_score,
                    source="facebook",
                    url=p.url,
                )
                for p in result.posts if p.text
            ]

        raise ValueError(f"Unknown source: {source}")
