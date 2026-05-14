from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class CategoryRead(BaseModel):
    id: UUID
    family_id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: float = 0.0
    unit: Optional[str] = None
    category_id: Optional[UUID] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None

class ProductRead(ProductBase):
    id: UUID
    family_id: UUID
    lemma: Optional[str] = None
    emoji: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
