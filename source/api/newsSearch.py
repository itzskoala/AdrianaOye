from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

from source.socialCollectors.news_collector import (
    Category,
    NewsCollector,
    NewsResult,
    SortBy,
)

load_dotenv(override=True)

router = APIRouter(prefix="/news", tags=["News"])
collector = NewsCollector()


@router.get("/search", response_model=NewsResult)
async def search_news(
    q: str = Query(..., description="Keywords or phrases to search"),
    language: str = Query(default="en", description="2-letter language code (en, es, fr…)"),
    sort_by: SortBy = Query(default="publishedAt"),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
):
    """Search the full news archive by keyword. Example: /news/search?q=climate+change"""
    try:
        return await collector.search(q, language, sort_by, limit, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/headlines", response_model=NewsResult)
async def top_headlines(
    q: str | None = Query(default=None, description="Optional keyword filter"),
    category: Category = Query(default="general"),
    country: str = Query(default="us", description="2-letter country code (us, gb, ca…)"),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get breaking top headlines by category and country. Example: /news/headlines?category=technology"""
    try:
        return await collector.headlines(q, category, country, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
