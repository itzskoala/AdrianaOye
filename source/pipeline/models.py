from datetime import datetime
from pydantic import BaseModel


class Post(BaseModel):
    """Unified post format — all collectors normalize to this before entering the pipeline."""
    text: str
    timestamp: datetime | None = None
    engagement: int = 0
    source: str
    url: str | None = None


class Topic(BaseModel):
    id: int
    keywords: list[str]
    post_count: int
    sample_texts: list[str]     # first 3 posts from this topic cluster


class TrendScore(BaseModel):
    topic_id: int
    keywords: list[str]
    velocity: float             # growth rate: recent half vs older half of the window
    spike: float                # burst signal: peak engagement vs average engagement
    total_engagement: int
    is_trending: bool


class TopicInsight(BaseModel):
    topic_id: int
    keywords: list[str]
    summary: str                # Ollama-generated narrative
    sentiment: str              # positive / negative / neutral / mixed
    key_insight: str            # one actionable takeaway
    trend: TrendScore


class PipelineResult(BaseModel):
    source: str
    query: str
    total_posts: int
    topics_found: int
    trending_count: int
    insights: list[TopicInsight]
    processed_at: datetime
