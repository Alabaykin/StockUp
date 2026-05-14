from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis
from app.core.config import settings

redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield
    await redis_client.close()

app = FastAPI(title="StockUp API", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "StockUp Backend"}

# TODO: Добавить роуты для API и инициализацию Aiogram
