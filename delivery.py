from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from APP.database import Base

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("food_donations.id"), nullable=False)
    shelter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    claimed_servings = Column(Integer, nullable=False)
    status = Column(String, default="Pending Dispatch")  # Pending Dispatch, In-Transit, Picked Up, Delivered
    pickup_otp = Column(String(4), nullable=False)
    drop_otp = Column(String(4), nullable=False)
    assigned_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_time = Column(DateTime, nullable=True)