from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import asyncio
from app.core.redis import get_redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    # Basic skeleton: just close for now
    await websocket.close(code=1000)
