from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.db.models import Product, User
from app.schemas.product import ProductRead, ProductCreate, ProductUpdate
from app.api.auth import get_current_user
from app.services.nlp import normalize_product_name, get_emoji_for_product

router = APIRouter()

@router.get("/", response_model=List[ProductRead])
async def get_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="User is not in a family")

    result = await db.execute(select(Product).where(Product.family_id == current_user.family_id))
    products = result.scalars().all()
    return products

@router.post("/", response_model=ProductRead)
async def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="User is not in a family")

    # NLP processing (use the user's preferred language)
    lang = current_user.language or "en"
    lemma = normalize_product_name(product_in.name, lang=lang)
    emoji = get_emoji_for_product(lemma, lang=lang)

    new_product = Product(
        family_id=current_user.family_id,
        category_id=product_in.category_id,
        name=product_in.name,
        lemma=lemma,
        emoji=emoji,
        description=product_in.description,
        quantity=product_in.quantity,
        unit=product_in.unit
    )
    
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    return new_product

@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: UUID,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="User is not in a family")

    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.family_id == current_user.family_id)
    )
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_in.model_dump(exclude_unset=True)
    
    lang = current_user.language or "en"
    if "name" in update_data:
        product.lemma = normalize_product_name(update_data["name"], lang=lang)
        product.emoji = get_emoji_for_product(product.lemma, lang=lang)

    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="User is not in a family")

    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.family_id == current_user.family_id)
    )
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)
    await db.commit()
    
    return {"status": "ok", "message": "Product deleted"}
