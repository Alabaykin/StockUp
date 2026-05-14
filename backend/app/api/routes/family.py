from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import secrets
import string

from app.db.database import get_db
from app.db.models import Family, User
from app.schemas.family import FamilyRead
from app.schemas.user import UserRead
from app.api.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class FamilyJoin(BaseModel):
    invite_code: str

def generate_invite_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.post("/create", response_model=FamilyRead)
async def create_family(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.family_id:
        raise HTTPException(status_code=400, detail="User already in a family. Leave first.")

    new_family = Family(invite_code=generate_invite_code())
    db.add(new_family)
    await db.commit()
    await db.refresh(new_family)

    current_user.family_id = new_family.id
    await db.commit()
    
    return new_family

@router.post("/join", response_model=FamilyRead)
async def join_family(
    data: FamilyJoin,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Family).where(Family.invite_code == data.invite_code))
    family = result.scalars().first()

    if not family:
        raise HTTPException(status_code=404, detail="Family not found with this invite code")

    current_user.family_id = family.id
    await db.commit()
    
    return family

@router.get("/me", response_model=FamilyRead)
async def get_my_family(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.family_id:
        raise HTTPException(status_code=404, detail="User is not in any family")

    result = await db.execute(select(Family).where(Family.id == current_user.family_id))
    family = result.scalars().first()
    
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
        
    return family
