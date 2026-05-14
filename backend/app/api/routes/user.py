from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.schemas.user import UserRead, UserLanguageUpdate
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.put("/language", response_model=UserRead)
async def update_language(
    data: UserLanguageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.language not in ("en", "ru"):
        raise HTTPException(status_code=400, detail="Supported languages: en, ru")

    current_user.language = data.language
    await db.commit()
    await db.refresh(current_user)
    return current_user
