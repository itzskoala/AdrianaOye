import os
from pathlib import Path

import asyncpg

_pool: asyncpg.Pool | None = None

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


async def init() -> None:
    """Create the connection pool and run schema migrations on startup."""
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=os.getenv("DATABASE_URL", "postgresql://adriana:adriana@localhost:5432/adriana"),
        min_size=2,
        max_size=10,
    )
    async with _pool.acquire() as conn:
        await conn.execute(SCHEMA_PATH.read_text())


async def close() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized — call db.postgres.init() first")
    return _pool
