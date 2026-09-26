from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from APP.database import get_db
from APP.models.donation import FoodDonation
from APP.models.delivery import Delivery
from APP.models.user import User
from APP.schemas.delivery_schema import FoodClaimRequest
from APP.utils.distance import calculate_haversine_distance
from APP.utils.transit_safety import validate_safe_transit
from APP.utils.otp_service import generate_verification_otp

router = APIRouter(prefix="/shelter", tags=["Shelter Endpoints"])

@router.post("/claim/{donation_id}")
def claim_food_portion(donation_id: int, payload: FoodClaimRequest, db: Session = Depends(get_db)):
    donation = db.query(FoodDonation).filter(FoodDonation.id == donation_id).first()
    if not donation or donation.status != "Available":
        raise HTTPException(status_code=400, detail="Donation is no longer available")

    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    if donation.expiry_time <= current_time:
        donation.status = "Expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Sorry, this food was spoiled and is no longer available.")

    if payload.requested_servings > donation.servings:
        raise HTTPException(status_code=400, detail="Requested portion exceeds available quantity")

    donor = db.query(User).filter(User.id == donation.donor_id).first()
    shelter = db.query(User).filter(User.id == payload.shelter_id).first()
    if not donor or not shelter:
        raise HTTPException(status_code=404, detail="Donor or Shelter profile not found")

    distance = calculate_haversine_distance(donor.latitude, donor.longitude, shelter.latitude, shelter.longitude)
    safety = validate_safe_transit(distance, donation.expiry_time)
    if not safety["is_safe"]:
        raise HTTPException(status_code=400, detail="Safety check failed: Expiry will lapse during transit window")

    pickup_otp = generate_verification_otp()
    drop_otp = generate_verification_otp()

    delivery = Delivery(
        donation_id=donation.id,
        shelter_id=shelter.id,
        claimed_servings=payload.requested_servings,
        status="Pending Dispatch",
        pickup_otp=pickup_otp,
        drop_otp=drop_otp
    )

    donation.servings -= payload.requested_servings
    if donation.servings == 0:
        donation.status = "Claimed"

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    return {
        "status": "success",
        "delivery_id": delivery.id,
        "distance_km": distance,
        "remaining_servings": donation.servings,
        "donor_phone": donor.phone,
        "receiver_phone": shelter.phone,
        "transit_assessment": safety
    }