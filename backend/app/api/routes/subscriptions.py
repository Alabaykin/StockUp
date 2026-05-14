from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.database import get_db
from app.db.models import ProductSubscription, User, Product
from app.schemas.subscription import SubscriptionToggle
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/toggle")
async def toggle_subscription(
    sub_in: SubscriptionToggle,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if product exists and belongs to family
    result = await db.execute(
        select(Product).where(
            Product.id == sub_in.product_id,
            Product.family_id == current_user.family_id
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if already subscribed
    result = await db.execute(
        select(ProductSubscription).where(
            ProductSubscription.user_id == current_user.telegram_id,
            ProductSubscription.product_id == sub_in.product_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        status = "unsubscribed"
    else:
        new_sub = ProductSubscription(
            user_id=current_user.telegram_id,
            product_id=sub_in.product_id
        )
        db.add(new_sub)
        status = "subscribed"
    
    await db.commit()
    return {"status": status}
