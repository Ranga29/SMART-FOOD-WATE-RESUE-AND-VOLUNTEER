from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from APP.database import get_db
from APP.models.delivery import Delivery
from APP.models.donation import FoodDonation
from APP.models.ledger import VolunteerPoints

router = APIRouter(prefix="/analytics", tags=["Analytics & Impact Reporting"])

@router.get("/summary")
def get_impact_summary(db: Session = Depends(get_db)):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    total_meals = db.query(func.sum(Delivery.claimed_servings))\
                    .filter(Delivery.status == "Delivered").scalar() or 0

    total_posted = db.query(func.sum(FoodDonation.servings)).scalar() or 0
    remaining_food = db.query(func.sum(FoodDonation.servings)).filter(FoodDonation.status == "Available").scalar() or 0
    total_carbon = db.query(func.sum(VolunteerPoints.carbon_saved_kg)).scalar() or 0.0
    total_distance = db.query(func.sum(VolunteerPoints.distance_km)).scalar() or 0.0

    daily_posted = db.query(func.sum(FoodDonation.servings))\
        .filter(FoodDonation.cooked_time >= today_start, FoodDonation.cooked_time < today_end).scalar() or 0

    daily_received = db.query(func.sum(Delivery.claimed_servings))\
        .filter(Delivery.status == "Delivered", Delivery.completed_time >= today_start, Delivery.completed_time < today_end).scalar() or 0

    return {
        "total_meals_saved": total_meals,
        "total_food_posted": total_posted,
        "remaining_food_servings": remaining_food,
        "total_carbon_offset_kg": round(total_carbon, 2),
        "total_transit_km": round(total_distance, 2),
        "today_food_posted": daily_posted,
        "today_food_received": daily_received,
        "today_remaining_food": remaining_food,
    }