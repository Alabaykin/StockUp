from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    family_id: Optional[UUID] = None
    language: str = "en"

class UserRead(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    family_id: Optional[UUID] = None
    language: str = "en"

    model_config = ConfigDict(from_attributes=True)

class UserLanguageUpdate(BaseModel):
    language: str  # "en" or "ru"

