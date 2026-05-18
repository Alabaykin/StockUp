from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.db.models import Product, User, ProductSubscription
from app.schemas.product import ProductRead, ProductCreate, ProductUpdate
from app.api.auth import get_current_user
from app.services.nlp import normalize_product_name, get_emoji_for_product
from app.core.redis import get_redis
import json

router = APIRouter()

@router.get("/", response_model=List[ProductRead])
async def get_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="User is not in a family")

    # Fetch products and check if current user is subscribed to each
    stmt = select(Product).where(Product.family_id == current_user.family_id)
    result = await db.execute(stmt)
    products = result.scalars().all()
    
    # Check subscriptions for current user
    sub_stmt = select(ProductSubscription.product_id).where(ProductSubscription.user_id == current_user.telegram_id)
    sub_result = await db.execute(sub_stmt)
    subscribed_ids = set(sub_result.scalars().all())
    
    for p in products:
        p.is_subscribed = p.id in subscribed_ids
        
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
    
    prev_quantity = product.quantity
    update_data = product_in.model_dump(exclude_unset=True)
    
    # If name changed, re-run NLP
    if "name" in update_data:
        lang = current_user.language or "en"
        update_data["lemma"] = normalize_product_name(update_data["name"], lang=lang)
        update_data["emoji"] = get_emoji_for_product(update_data["lemma"], lang=lang)

    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    
    # Check if quantity hit zero to notify family members
    if product.quantity == 0:
        # Fetch subscribers for this product
        sub_stmt = select(ProductSubscription.user_id).where(ProductSubscription.product_id == product.id)
        sub_result = await db.execute(sub_stmt)
        subscribers = sub_result.scalars().all()

        r = await get_redis()
        if r:
            payload = {
                "type": "out_of_stock",
                "product_name": product.name,
                "product_emoji": product.emoji,
                "family_id": str(product.family_id),
                "subscribers": subscribers
            }
            await r.publish("notifications", json.dumps(payload))

    # Check if quantity increased (product purchased / back in stock)
    elif product.quantity > (prev_quantity or 0.0):
        r = await get_redis()
        if r:
            notified_users = set()
            
            # Check if this product was requested
            req_key = f"product:{product.id}:requested"
            was_requested = await r.exists(req_key)
            if was_requested:
                await r.delete(req_key)
                
                # Get all family members to notify
                members_stmt = select(User.telegram_id).where(User.family_id == product.family_id)
                members_result = await db.execute(members_stmt)
                members = members_result.scalars().all()
                
                # Exclude the buyer (current_user)
                req_subscribers = [m for m in members if m != current_user.telegram_id]
                if req_subscribers:
                    payload = {
                        "type": "request_fulfilled",
                        "product_name": product.name,
                        "product_emoji": product.emoji,
                        "family_id": str(product.family_id),
                        "subscribers": req_subscribers,
                        "user_name": current_user.first_name or current_user.username or "Кто-то"
                    }
                    await r.publish("notifications", json.dumps(payload))
                    notified_users.update(req_subscribers)
            
            # Check if product is back in stock (went from 0/None to >0)
            if (prev_quantity == 0 or prev_quantity is None) and product.quantity > 0:
                # Get subscribers to notify (back in stock)
                sub_stmt = select(ProductSubscription.user_id).where(ProductSubscription.product_id == product.id)
                sub_result = await db.execute(sub_stmt)
                subscribers = sub_result.scalars().all()
                
                # Exclude buyer and people who already got request_fulfilled
                bis_subscribers = [s for s in subscribers if s != current_user.telegram_id and s not in notified_users]
                if bis_subscribers:
                    payload = {
                        "type": "back_in_stock",
                        "product_name": product.name,
                        "product_emoji": product.emoji,
                        "family_id": str(product.family_id),
                        "subscribers": bis_subscribers,
                        "user_name": current_user.first_name or current_user.username or "Кто-то"
                    }
                    await r.publish("notifications", json.dumps(payload))

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

@router.post("/{product_id}/request")
async def request_product(
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

    # Get all family members to notify
    members_stmt = select(User.telegram_id).where(User.family_id == current_user.family_id)
    members_result = await db.execute(members_stmt)
    members = members_result.scalars().all()

    r = await get_redis()
    if r:
        # Mark as requested in Redis (7 days expiration)
        await r.setex(f"product:{product.id}:requested", 604800, "1")

        payload = {
            "type": "shopping_request",
            "product_name": product.name,
            "product_emoji": product.emoji,
            "family_id": str(product.family_id),
            "subscribers": members,
            "user_name": current_user.first_name or current_user.username or "Someone"
        }
        await r.publish("notifications", json.dumps(payload))

    return {"status": "request_sent"}