from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    family_id: Optional[UUID] = None

class UserRead(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    family_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
