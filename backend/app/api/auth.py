import hmac
import hashlib
from urllib.parse import unquote
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.db.database import get_db
from app.db.models import User
import json


def validate_telegram_data(init_data: str, bot_token: str) -> dict:
    try:
        # Manual parsing because parse_qsl uses unquote_plus (which breaks some hashes)
        # and we must handle empty values properly
        parsed_data = {}
        for pair in init_data.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                parsed_data[k] = unquote(v)
            else:
                parsed_data[pair] = ""
                
        if "hash" not in parsed_data:
            return {"error": f"No hash in initData (fields: {list(parsed_data.keys())})"}
            # return None

        hash_from_telegram = parsed_data.pop("hash")
        
        # Sort keys alphabetically
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )
        
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash != hash_from_telegram:
            # return None
            # We return exactly what failed so it appears in the Web App Toast notification!
            return {"error": f"HMAC mismatch. calc={calculated_hash[:5]} recv={hash_from_telegram[:5]}. init={init_data[:20]}"}
            
        user_data = json.loads(parsed_data.get("user", "{}"))
        return user_data
    # except Exception:
    #     return None
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

async def get_current_user(
    x_tg_init_data: str = Header(..., description="Telegram initData string"),
    db: AsyncSession = Depends(get_db)
) -> User:
    user_data = validate_telegram_data(x_tg_init_data, settings.BOT_TOKEN)
    if not user_data or "id" not in user_data:
        # Allow dev_mode if token is empty, None, or the default placeholder
        if x_tg_init_data == "dev_mode" and settings.BOT_TOKEN in ["", None, "YOUR_TELEGRAM_BOT_TOKEN"]:
             user_data = {"id": 111111111, "first_name": "DevUser", "username": "dev"}
        else:
            # raise HTTPException(status_code=401, detail=f"Invalid Telegram initData")
            err_msg = user_data.get("error") if isinstance(user_data, dict) else "Unknown"
            raise HTTPException(status_code=401, detail=f"Invalid Telegram initData. Reason: {err_msg}")
    
    telegram_id = user_data["id"]
    
    # Get or create user
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()
    
    if not user:
        user = User(
            telegram_id=telegram_id,
            first_name=user_data.get("first_name"),
            username=user_data.get("username")
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user
