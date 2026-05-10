from fastapi import APIRouter, HTTPException, Query

from source.socialCollectors.reddit_collector import RedditCollector, RedditResult, Sort

router = APIRouter(prefix="/reddit", tags=["Reddit"])
collector = RedditCollector()


@router.get("/search", response_model=RedditResult)
async def search_reddit(
    q: str = Query(..., description="Keyword or phrase to search"),
    sort: Sort = Query(default="new"),
    limit: int = Query(default=25, ge=1, le=100),
):
    """Search all of Reddit by keyword. Example: /reddit/search?q=machine+learning"""
    try:
        return await collector.search(q, sort, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/r/{subreddit}", response_model=RedditResult)
async def get_subreddit(
    subreddit: str,
    sort: Sort = Query(default="hot"),
    limit: int = Query(default=25, ge=1, le=100),
):
    """Get posts from a specific subreddit. Example: /reddit/r/MachineLearning?sort=new"""
    try:
        return await collector.subreddit(subreddit, sort, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
