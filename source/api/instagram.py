#this is where the actual scrapping logic is implemented, using Apify's Instagram Scraper actor
#this is also where the FastAPI is implemneted.

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

from source.socialCollectors.instagram_collector import InstagramCollector, ScrapeResult

load_dotenv(override=True)

router = APIRouter(prefix="/instagram", tags=["Instagram"])
collector = InstagramCollector()


@router.get("/hashtag/{hashtag}", response_model=ScrapeResult)
async def get_by_hashtag(
    hashtag: str,
    limit: int = Query(default=20, ge=1, le=50, description="Number of posts to fetch"),
):
    """Scrape recent posts for a given hashtag. Example: /instagram/hashtag/travel"""
    try:
        return await collector.scrape_hashtag(hashtag, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{username}", response_model=ScrapeResult)
async def get_by_profile(
    username: str,
    limit: int = Query(default=20, ge=1, le=50, description="Number of posts to fetch"),
):
    """Scrape recent posts from a public Instagram profile. Example: /instagram/profile/natgeo"""
    try:
        return await collector.scrape_profile(username, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

