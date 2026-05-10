from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

from source.socialCollectors.facebook_collector import FacebookCollector, ScrapeResult

load_dotenv(override=True)

router = APIRouter(prefix="/facebook", tags=["Facebook"])
collector = FacebookCollector()


@router.get("/page/{page}", response_model=ScrapeResult)
async def get_page_posts(
    page: str,
    limit: int = Query(default=20, ge=1, le=50, description="Number of posts to fetch"),
):
    """Scrape recent posts from a public Facebook page. Example: /facebook/page/nasa"""
    try:
        return await collector.scrape_page(page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
