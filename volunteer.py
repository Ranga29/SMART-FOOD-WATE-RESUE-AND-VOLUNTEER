from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from APP.database import get_db
from APP.models.delivery import Delivery
from APP.models.donation import FoodDonation
from APP.models.user import User
from APP.models.ledger import VolunteerPoints
from APP.schemas.delivery_schema import DeliveryTaskAccept, OTPVerifyRequest
from APP.utils.distance import calculate_haversine_distance

router = APIRouter(prefix="/volunteer", tags=["Volunteer Endpoints"])

def serialize_task(task: Delivery, db: Session):
    donor = db.query(User).join(FoodDonation, FoodDonation.donor_id == User.id)\
                         .filter(FoodDonation.id == task.donation_id).first()
    shelter = db.query(User).filter(User.id == task.shelter_id).first()
    dist = calculate_haversine_distance(donor.latitude, donor.longitude, shelter.latitude, shelter.longitude)
    eta_minutes = max(10, int((dist / 18) * 60))
    return {
        "delivery_id": task.id,
        "claimed_servings": task.claimed_servings,
        "distance_km": dist,
        "eta_minutes": eta_minutes,
        "pickup_name": donor.name,
        "pickup_phone": donor.phone,
        "pickup_lat": donor.latitude,
        "pickup_lon": donor.longitude,
        "drop_name": shelter.name,
        "drop_phone": shelter.phone,
        "drop_lat": shelter.latitude,
        "drop_lon": shelter.longitude,
        "status": task.status,
    }

@router.get("/available-tasks")
def get_available_dispatch_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Delivery).filter(Delivery.status == "Pending Dispatch").all()
    return [serialize_task(task, db) for task in tasks]

@router.get("/my-active-task/{volunteer_id}")
def get_active_volunteer_task(volunteer_id: int, db: Session = Depends(get_db)):
    task = db.query(Delivery).filter(
        Delivery.volunteer_id == volunteer_id,
        Delivery.status.in_(["In-Transit", "Picked Up"]),
    ).order_by(Delivery.id.desc()).first()
    if not task:
        return None

    serialized_task = serialize_task(task, db)
    serialized_task["pickup_otp"] = task.pickup_otp
    serialized_task["drop_otp"] = task.drop_otp
    return serialized_task

@router.post("/accept-task")
def accept_dispatch_task(payload: DeliveryTaskAccept, db: Session = Depends(get_db)):
    task = db.query(Delivery).filter(Delivery.id == payload.delivery_id).first()
    if not task or task.status != "Pending Dispatch":
        raise HTTPException(status_code=400, detail="Task already accepted or invalid")

    task.volunteer_id = payload.volunteer_id
    task.status = "In-Transit"
    db.commit()
    return {
        "status": "success",
        "message": "Delivery assigned to volunteer",
        "delivery_id": task.id,
        "pickup_otp": task.pickup_otp,
        "drop_otp": task.drop_otp,
    }

@router.post("/verify-otp")
def verify_handoff_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    task = db.query(Delivery).filter(Delivery.id == payload.delivery_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Delivery task not found")

    if payload.step == "pickup":
        if payload.otp != task.pickup_otp:
            raise HTTPException(status_code=400, detail="Invalid Pickup OTP token")
        task.status = "Picked Up"
        db.commit()
        return {
            "status": "success",
            "message": "Pickup confirmed. Route is live to the receiver.",
            "pickup_otp": task.pickup_otp,
            "drop_otp": task.drop_otp,
        }

    elif payload.step == "drop":
        if payload.otp != task.drop_otp:
            raise HTTPException(status_code=400, detail="Invalid Drop OTP token")

        task.status = "Delivered"
        task.completed_time = datetime.now(timezone.utc)

        donor = db.query(User).join(FoodDonation, FoodDonation.donor_id == User.id)\
                             .filter(FoodDonation.id == task.donation_id).first()
        shelter = db.query(User).filter(User.id == task.shelter_id).first()
        dist = calculate_haversine_distance(donor.latitude, donor.longitude, shelter.latitude, shelter.longitude)

        points = max(3, int((dist / 5) * 3))
        carbon = round(task.claimed_servings * 0.4 * 2.5, 2)

        ledger_entry = VolunteerPoints(
            volunteer_id=task.volunteer_id,
            points=points,
            distance_km=dist,
            carbon_saved_kg=carbon
        )
        db.add(ledger_entry)
        db.commit()

        return {
            "status": "success",
            "message": "Delivery completed successfully",
            "points_earned": points,
            "carbon_saved_kg": carbon,
            "pickup_otp": task.pickup_otp,
            "drop_otp": task.drop_otp
        }

    raise HTTPException(status_code=400, detail="Invalid handoff step specification")