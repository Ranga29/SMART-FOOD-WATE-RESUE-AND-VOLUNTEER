from pydantic import BaseModel, EmailStr
from typing import Literal

class UserCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    role: Literal["donor", "shelter", "volunteer"]
    phone: str
    latitude: float
    longitude: float

class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    phone: str
    role: Literal["donor", "shelter", "volunteer"]