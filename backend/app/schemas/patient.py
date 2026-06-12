"""Patient schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PatientResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: list[str] = []
    allergies: list[str] = []
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PatientUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: Optional[list[str]] = None
    allergies: Optional[list[str]] = None
