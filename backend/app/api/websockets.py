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
        
    redis_client = await get_redis()
    pubsub = redis_client.pubsub()
    channel_name = f"family:{user.family_id}:updates"
    
    await pubsub.subscribe(channel_name)
    
    try:
        # We need two tasks: one to read from websocket (to detect disconnects),
        # one to read from redis and send to websocket.
        
        async def read_from_ws():
            try:
                while True:
                    # Cloudflare might drop inactive connections. 
                    # We can handle ping/pong here if needed.
                    data = await websocket.receive_text()
                    if data == "ping":
                        await websocket.send_text("pong")
            except WebSocketDisconnect:
                pass

        async def read_from_redis():
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        await websocket.send_text(message["data"])
            except Exception:
                pass

        ws_task = asyncio.create_task(read_from_ws())
        redis_task = asyncio.create_task(read_from_redis())
        
        done, pending = await asyncio.wait(
            [ws_task, redis_task], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for task in pending:
            task.cancel()
            
    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()
