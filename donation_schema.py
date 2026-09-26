from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FoodDonationCreate(BaseModel):
    donor_id: int
    food_name: str
    servings: int = Field(gt=0)
    expiry_time: datetime
    photo_url: Optional[str] = None


class FoodDonationResponse(FoodDonationCreate):
    id: int
    status: str
    cooked_time: datetime

    class Config:
        from_attributes = True

class FoodClaimRequest(BaseModel):
    shelter_id: int
    requested_servings: int = Field(gt=0)

class DeliveryTaskAccept(BaseModel):
    volunteer_id: int
    delivery_id: int

class OTPVerifyRequest(BaseModel):
    delivery_id: int
    otp: str
    step: str  # "pickup" or "drop"