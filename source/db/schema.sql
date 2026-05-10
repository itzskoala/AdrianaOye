CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Raw social posts — deduplicated by URL so the same post is never stored twice
CREATE TABLE IF NOT EXISTS posts (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    source       VARCHAR(50) NOT NULL,
    url          TEXT        UNIQUE NOT NULL,
    text         TEXT        NOT NULL,
    engagement   INTEGER     DEFAULT 0,
    post_ts      TIMESTAMPTZ,
    fetched_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- One row per unique topic (identified by its top keyword fingerprint)
CREATE TABLE IF NOT EXISTS topics (
    fingerprint  TEXT        PRIMARY KEY,   -- e.g. "ai:llm:openai"
    keywords     TEXT[]      NOT NULL,
    first_seen   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trend score snapshot every time the pipeline runs — this is the history
CREATE TABLE IF NOT EXISTS trend_snapshots (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_fingerprint TEXT        NOT NULL REFERENCES topics(fingerprint),
    source            VARCHAR(50) NOT NULL,
    query             TEXT        NOT NULL,
    velocity          FLOAT       NOT NULL,
    spike             FLOAT       NOT NULL,
    total_engagement  INTEGER     NOT NULL,
    post_count        INTEGER     NOT NULL,
    is_trending       BOOLEAN     NOT NULL,
    snapshot_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- AI-generated insights per topic run — avoid calling Ollama twice for the same topic
CREATE TABLE IF NOT EXISTS insights (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_fingerprint TEXT        NOT NULL REFERENCES topics(fingerprint),
    summary           TEXT        NOT NULL,
    sentiment         VARCHAR(20) NOT NULL,
    key_insight       TEXT        NOT NULL,
    generated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_snapshots_fingerprint ON trend_snapshots(topic_fingerprint);
CREATE INDEX IF NOT EXISTS idx_snapshots_at          ON trend_snapshots(snapshot_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_source          ON posts(source);
CREATE INDEX IF NOT EXISTS idx_posts_fetched         ON posts(fetched_at DESC);
