"""Doctor schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DoctorResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    specialization: str
    qualification: Optional[str] = None
    experience: int
    consultation_fee: float
    bio: Optional[str] = None
    availability_status: bool
    rating: float
    total_consultations: int
    avatar: Optional[str] = None

    model_config = {"from_attributes": True}


class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[int] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    availability_status: Optional[bool] = None


class DoctorEarnings(BaseModel):
    total_earnings: float
    daily_earnings: float
    monthly_earnings: float
    total_consultations: int
    upcoming_appointments: int


class DoctorMedicineCreate(BaseModel):
    medicine_name: str
    dosage_template: Optional[str] = None
    instructions_template: Optional[str] = None


class DoctorMedicineResponse(BaseModel):
    id: int
    doctor_id: int
    medicine_name: str
    dosage_template: Optional[str] = None
    instructions_template: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DoctorMedicineUpdate(BaseModel):
    medicine_name: Optional[str] = None
    dosage_template: Optional[str] = None
    instructions_template: Optional[str] = None
