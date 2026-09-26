from sqlalchemy import Column, Integer, Float, ForeignKey
from APP.database import Base

class VolunteerPoints(Base):
    __tablename__ = "volunteer_points"

    id = Column(Integer, primary_key=True, index=True)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points = Column(Integer, default=0)
    distance_km = Column(Float, default=0.0)
    carbon_saved_kg = Column(Float, default=0.0)