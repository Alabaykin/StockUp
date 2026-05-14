from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import redis.asyncio as redis
import os
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

# ── Serve frontend static files ──
# In Docker: /frontend is mounted; locally: fallback to relative path
FRONTEND_DIR = "/frontend" if os.path.isdir("/frontend") else os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend"
)

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
