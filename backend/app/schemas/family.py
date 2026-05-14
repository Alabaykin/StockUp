from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class FamilyCreate(BaseModel):
    pass # Семья создается автоматически, нам не нужны параметры

class FamilyRead(BaseModel):
    id: UUID
    invite_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
