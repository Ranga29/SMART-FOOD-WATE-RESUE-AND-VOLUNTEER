from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from APP.database import Base

class FoodDonation(Base):
    __tablename__ = "food_donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_name = Column(String, nullable=False)
    servings = Column(Integer, nullable=False)
    cooked_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expiry_time = Column(DateTime, nullable=False)
    status = Column(String, default="Available")  # Available, Claimed, Delivered
    photo_url = Column(String, nullable=True)