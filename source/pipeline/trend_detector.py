from source.pipeline.models import Post, Topic, TrendScore

_TRENDING_VELOCITY = 0.25       # topic grew >25% faster in recent half vs older half
_TRENDING_SPIKE    = 1.75       # peak engagement is 1.75× the topic's own average


class TrendDetector:
    def score(
        self,
        posts: list[Post],
        topics: list[Topic],
        doc_topic_ids: list[int],
    ) -> list[TrendScore]:
        scores = []
        for topic in topics:
            topic_posts = [
                posts[i]
                for i, tid in enumerate(doc_topic_ids)
                if tid == topic.id
            ]
            scores.append(self._score_topic(topic, topic_posts))
        return scores

    def _score_topic(self, topic: Topic, posts: list[Post]) -> TrendScore:
        total_engagement = sum(p.engagement for p in posts)

        velocity = self._velocity(posts)
        spike    = self._spike(posts)

        return TrendScore(
            topic_id=topic.id,
            keywords=topic.keywords,
            velocity=round(velocity, 3),
            spike=round(spike, 3),
            total_engagement=total_engagement,
            is_trending=(velocity >= _TRENDING_VELOCITY or spike >= _TRENDING_SPIKE),
        )

    def _velocity(self, posts: list[Post]) -> float:
        """
        Growth rate: split posts chronologically into two halves,
        compare counts. Falls back to 0.0 if no timestamps.
        """
        timed = sorted(
            [p for p in posts if p.timestamp],
            key=lambda p: p.timestamp,
        )
        if len(timed) < 2:
            return 0.0

        mid   = len(timed) // 2
        older = timed[:mid]
        newer = timed[mid:]

        if not older:
            return 0.0

        # (newer - older) / older  →  positive = growing, negative = shrinking
        return (len(newer) - len(older)) / len(older)

    def _spike(self, posts: list[Post]) -> float:
        """
        Burst signal: how much does the peak-engagement post exceed
        the average engagement for this topic cluster?
        """
        scores = [p.engagement for p in posts if p.engagement > 0]
        if not scores:
            return 0.0

        avg = sum(scores) / len(scores)
        if avg == 0:
            return 0.0

        return max(scores) / avg
