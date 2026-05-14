from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis
from app.core.config import settings

from app.api.routes import family, products, user

redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield
    await redis_client.close()

app = FastAPI(title="StockUp API", lifespan=lifespan)

app.include_router(family.router, prefix="/api/v1/family", tags=["Family"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "StockUp Backend"}

