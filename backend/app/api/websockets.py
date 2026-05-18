from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import asyncio
from app.core.redis import get_redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

from app.api.auth import validate_telegram_data
from app.core.config import settings
from sqlalchemy.future import select
from app.db.models import User

router = APIRouter()

async def get_ws_user(websocket: WebSocket, db: AsyncSession):
    # Expecting initData in query params: ?initData=...
    init_data = websocket.query_params.get("initData")
    if not init_data:
        await websocket.close(code=4001)
        return None
        
    user_data = validate_telegram_data(init_data, settings.BOT_TOKEN)
    if not user_data or "id" not in user_data:
        if init_data == "dev_mode" and settings.BOT_TOKEN in ["", None, "TELEGRAM_BOT_TOKEN"]:
            user_data = {"id": 111111111}
        else:
            await websocket.close(code=4001)
            return None
            
    result = await db.execute(select(User).where(User.telegram_id == user_data["id"]))
    user = result.scalars().first()
    if not user or not user.family_id:
        await websocket.close(code=4003)
        return None
        
    return user

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    
    user = await get_ws_user(websocket, db)
    if not user:
        return
        
    # Basic skeleton: just close for now
    await websocket.close(code=1000)
