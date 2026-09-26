import asyncio
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from APP.database import engine, Base, SessionLocal
from APP.models.donation import FoodDonation
from APP.models.user import User
from APP.routes import analytics, auth, donor, shelter, volunteer

Base.metadata.create_all(bind=engine)


def ensure_demo_users():
    db = SessionLocal()
    demo_users = [
        {
            "id": 1,
            "name": "Joy University Hostel Mess #2",
            "email": "mess2@joyuniversity.edu.in",
            "role": "donor",
            "phone": "+919876543210",
            "latitude": 12.9716,
            "longitude": 79.1585,
        },
        {
            "id": 2,
            "name": "Karuna Orphanage Home",
            "email": "contact@karunahome.org",
            "role": "shelter",
            "phone": "+919876543211",
            "latitude": 12.9249,
            "longitude": 79.1352,
        },
        {
            "id": 3,
            "name": "Campus Volunteer Rider",
            "email": "volunteer1@joyuniversity.edu.in",
            "role": "volunteer",
            "phone": "+919876543212",
            "latitude": 12.9650,
            "longitude": 79.1500,
        },
    ]

    try:
        for user_data in demo_users:
            if db.query(User).filter(User.id == user_data["id"]).first() is None:
                db.add(User(**user_data))
        db.commit()
    finally:
        db.close()


ensure_demo_users()


async def cleanup_expired_donations():
    while True:
        db = SessionLocal()
        try:
            expiry_cutoff = (datetime.now(timezone.utc) - timedelta(minutes=5)).replace(tzinfo=None)
            db.query(FoodDonation).filter(
                FoodDonation.status == "Available",
                FoodDonation.expiry_time <= expiry_cutoff,
            ).update({FoodDonation.status: "Expired"}, synchronize_session=False)
            db.commit()
        finally:
            db.close()
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(_: FastAPI):
    cleanup_task = asyncio.create_task(cleanup_expired_donations())
    try:
        yield
    finally:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Smart Hyperlocal Food Waste Rescue Engine",
    description="Backend microservices for routing institutional surplus food to shelters",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(donor.router)
app.include_router(shelter.router)
app.include_router(volunteer.router)
app.include_router(analytics.router)

@app.get("/")
def root_health():
    return {"status": "online", "system": "Food Rescue Platform Backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)