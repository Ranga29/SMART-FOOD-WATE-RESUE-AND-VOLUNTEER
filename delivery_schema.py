from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class FoodClaimRequest(BaseModel):
    shelter_id: int
    requested_servings: int = Field(gt=0)

class DeliveryTaskAccept(BaseModel):
    volunteer_id: int
    delivery_id: int

class OTPVerifyRequest(BaseModel):
    delivery_id: int
    otp: str
    step: Literal["pickup", "drop"]

class DeliveryResponse(BaseModel):
    id: int
    donation_id: int
    shelter_id: int
    volunteer_id: Optional[int]
    claimed_servings: int
    status: str
    assigned_time: datetime
    completed_time: Optional[datetime]

    class Config:
        from_attributes = True