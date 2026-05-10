from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv(override=True)

from fastapi import FastAPI

from source.db import postgres, redis_client
from source.api.instagram import router as instagram_router
from source.api.newsSearch import router as news_router
from source.api.facebook import router as facebook_router
from source.api.reddit import router as reddit_router
from source.api.pipeline import router as pipeline_router
from source.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await postgres.init()       # create pool + run schema.sql (idempotent)
    yield
    await postgres.close()
    await redis_client.close()


app = FastAPI(title="Social Listening API", version="0.1.0", lifespan=lifespan)

app.include_router(instagram_router)
app.include_router(news_router)
app.include_router(facebook_router)
app.include_router(reddit_router)
app.include_router(pipeline_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Social Listening API is running"}
