import os

import httpx

from source.pipeline.models import Post, Topic, TopicInsight, TrendScore

OLLAMA_BASE  = "http://localhost:11434"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


class InsightsEngine:
    async def analyze(
        self,
        posts: list[Post],
        topics: list[Topic],
        trends: list[TrendScore],
        doc_topic_ids: list[int],
    ) -> list[TopicInsight]:
        trend_map = {t.topic_id: t for t in trends}
        topic_map = {t.id: t for t in topics}

        trending = [t for t in trends if t.is_trending]

        insights = []
        for trend in trending:
            topic = topic_map[trend.topic_id]
            topic_posts = [
                posts[i]
                for i, tid in enumerate(doc_topic_ids)
                if tid == topic.id
            ]
            insight = await self._analyze_topic(topic, trend, topic_posts)
            insights.append(insight)

        return insights

    async def _analyze_topic(
        self,
        topic: Topic,
        trend: TrendScore,
        posts: list[Post],
    ) -> TopicInsight:
        sample = "\n".join(f"- {p.text[:200]}" for p in posts[:8])
        keywords_str = ", ".join(topic.keywords[:6])

        prompt = f"""You are a social media analyst for a brand monitoring tool.

        Topic keywords: {keywords_str}

        Sample posts from this topic:
        {sample}

        Respond in exactly this format (no extra text):
        SUMMARY: <2-3 sentences describing what people are saying>
        SENTIMENT: <one word: positive, negative, neutral, or mixed>
        INSIGHT: <one actionable insight for a brand monitoring this topic>"""

        response_text = await self._call_ollama(prompt)
        summary, sentiment, insight = self._parse_response(response_text)

        return TopicInsight(
            topic_id=topic.id,
            keywords=topic.keywords,
            summary=summary,
            sentiment=sentiment,
            key_insight=insight,
            trend=trend,
        )

    async def _call_ollama(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{OLLAMA_BASE}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    def _parse_response(self, text: str) -> tuple[str, str, str]:
        summary   = self._extract("SUMMARY", text)
        sentiment = self._extract("SENTIMENT", text).lower()
        insight   = self._extract("INSIGHT", text)

        valid_sentiments = {"positive", "negative", "neutral", "mixed"}
        if sentiment not in valid_sentiments:
            sentiment = "mixed"

        return summary, sentiment, insight

    def _extract(self, label: str, text: str) -> str:
        for line in text.splitlines():
            if line.startswith(f"{label}:"):
                return line[len(label) + 1:].strip()
        return ""
