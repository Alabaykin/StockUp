from pydantic import BaseModel, UUID4

class SubscriptionToggle(BaseModel):
    product_id: UUID4
