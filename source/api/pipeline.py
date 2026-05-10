from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from source.db.store import store
from source.pipeline.models import PipelineResult
from source.pipeline.pipeline import Pipeline, Source

load_dotenv(override=True)

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])
pipeline = Pipeline()


class AnalyzeRequest(BaseModel):
    source: Source
    query: str
    limit: int = 50


@router.post("/analyze", response_model=PipelineResult)
async def analyze(req: AnalyzeRequest):
    """
    Fetch posts from a source, run topic modeling + trend detection + AI insights.
    source: reddit | instagram | facebook | news
    """
    try:
        return await pipeline.run(req.source, req.query, req.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending(limit: int = Query(default=10, ge=1, le=50)):
    """Return the top trending topics across all sources — read from Redis, no DB hit."""
    try:
        return await store.get_top_trending(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{fingerprint}")
async def get_topic_history(fingerprint: str, limit: int = Query(default=30, ge=1, le=100)):
    """Return the trend snapshot history for a topic fingerprint (e.g. 'ai:llm:openai')."""
    try:
        return await store.get_topic_history(fingerprint, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
