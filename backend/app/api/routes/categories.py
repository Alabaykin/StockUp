from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.database import get_db
from app.db.models import Category, User
from app.schemas.category import CategoryRead, CategoryCreate
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CategoryRead])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="User not in a family")
    
    result = await db.execute(
        select(Category).where(Category.family_id == current_user.family_id)
    )
    return result.scalars().all()

@router.post("/", response_model=CategoryRead)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="User not in a family")
    
    category = Category(
        name=category_in.name,
        family_id=current_user.family_id
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if category exists and belongs to family
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.family_id == current_user.family_id
        )
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await db.delete(category)
    await db.commit()
    return {"status": "ok"}
