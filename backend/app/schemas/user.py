"""User schemas — signup, login, response."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: str
    role: str = "patient"  # patient, doctor, admin

    # Doctor-specific fields (only when role=doctor)
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[int] = None
    consultation_fee: Optional[float] = 500.0
    bio: Optional[str] = None

    # Patient-specific fields (only when role=patient)
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: Optional[list[str]] = []
    allergies: Optional[list[str]] = []


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    created_at: Optional[datetime] = None

    # Profile IDs
    doctor_id: Optional[int] = None
    patient_id: Optional[int] = None

    # Extended profile (included when available)
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[int] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    availability_status: Optional[bool] = None
    total_earnings: Optional[float] = None
    rating: Optional[float] = None
    total_consultations: Optional[int] = None
    avatar: Optional[str] = None

    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: Optional[list[str]] = []
    allergies: Optional[list[str]] = []

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[int] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    availability_status: Optional[bool] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: Optional[list[str]] = None
    allergies: Optional[list[str]] = None
