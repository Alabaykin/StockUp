from pydantic import BaseModel, UUID4
from typing import Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: UUID4
    family_id: UUID4

    class Config:
        from_attributes = True
