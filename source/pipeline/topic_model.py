import asyncio
from concurrent.futures import ThreadPoolExecutor

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

from source.pipeline.models import Post, Topic

# all-MiniLM-L6-v2: 80MB, fast, strong English semantic understanding
_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
_MIN_DOCS = 5       # BERTopic needs enough docs to find clusters


class TopicModeler:
    def __init__(self):
        self._embedder = SentenceTransformer(_EMBEDDING_MODEL)
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def fit(self, posts: list[Post]) -> tuple[list[Topic], list[int]]:
        """
        Returns (topics, doc_topic_ids).
        doc_topic_ids[i] is the topic ID assigned to posts[i]. -1 = outlier.
        Runs in a thread pool — BERTopic.fit_transform is synchronous and CPU-heavy.
        """
        docs = [p.text for p in posts]

        if len(docs) < _MIN_DOCS:
            raise ValueError(f"Need at least {_MIN_DOCS} posts to model topics, got {len(docs)}")

        loop = asyncio.get_event_loop()
        topics_raw, doc_ids = await loop.run_in_executor(
            self._executor,
            lambda: self._fit_sync(docs),
        )

        topics = []
        for row in topics_raw.itertuples():
            if row.Topic == -1:
                continue    # -1 is BERTopic's "outlier" bucket — no coherent theme

            # Representation is a list of (word, score) tuples
            keywords = [word for word, _ in row.Representation] if row.Representation else []

            # Sample up to 3 representative texts from this topic
            samples = [
                posts[i].text[:120]
                for i, tid in enumerate(doc_ids)
                if tid == row.Topic
            ][:3]

            topics.append(Topic(
                id=row.Topic,
                keywords=keywords[:8],
                post_count=row.Count,
                sample_texts=samples,
            ))

        return topics, list(doc_ids)

    def _fit_sync(self, docs: list[str]):
        model = BERTopic(
            embedding_model=self._embedder,
            language="english",
            calculate_probabilities=False,  # faster — we don't need per-doc confidence
            verbose=False,
            min_topic_size=2,               # allow small clusters for limited data sets
        )
        doc_ids, _ = model.fit_transform(docs)
        topic_info = model.get_topic_info()
        return topic_info, doc_ids
