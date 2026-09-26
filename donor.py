import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from APP.database import get_db
from APP.models.donation import FoodDonation
from APP.schemas.donation_schema import FoodDonationCreate, FoodDonationResponse

router = APIRouter(prefix="/donor", tags=["Donor Endpoints"])
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/post-surplus", response_model=FoodDonationResponse)
def post_surplus(payload: FoodDonationCreate, db: Session = Depends(get_db)):
    donation = FoodDonation(**payload.model_dump(), status="Available")
    db.add(donation)
    db.commit()
    db.refresh(donation)
    return donation

@router.post("/upload-photo/{donation_id}")
def upload_packing_photo(donation_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    donation = db.query(FoodDonation).filter(FoodDonation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation record not found")

    file_path = os.path.join(UPLOAD_DIR, f"donation_{donation_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    donation.photo_url = file_path
    db.commit()
    return {"status": "success", "photo_url": file_path}

@router.get("/active-listings", response_model=list[FoodDonationResponse])
def get_active_listings(db: Session = Depends(get_db)):
    return db.query(FoodDonation).filter(FoodDonation.status == "Available").all()