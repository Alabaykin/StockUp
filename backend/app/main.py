from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import redis.asyncio as redis
import os
from app.core.config import settings

import asyncio
import logging
from app.api.routes import family, products, user, categories, subscriptions
from app.core.bot import start_bot
from app.core.redis import init_redis

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Redis
    r_client = await init_redis()
    
    # Start Telegram Bot in background
    bot_task = asyncio.create_task(start_bot())
    
    yield
    
    # Shutdown
    bot_task.cancel()
    await r_client.close()

app = FastAPI(title="StockUp API", lifespan=lifespan)

from app.api import websockets

app.include_router(family.router, prefix="/api/v1/family", tags=["Family"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])
app.include_router(websockets.router, prefix="/api/v1", tags=["WebSockets"])

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
        return FileResponse(
            os.path.join(FRONTEND_DIR, "index.html"),
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
