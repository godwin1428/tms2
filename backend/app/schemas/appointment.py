"""Appointment schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: date
    start_time: str  # "09:00"
    end_time: Optional[str] = None  # auto-calculated if not provided


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    start_time: str
    end_time: str
    status: str
    payment_status: str
    meeting_room_id: Optional[str] = None
    created_at: Optional[datetime] = None

    # Joined data
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    patient_avatar: Optional[str] = None
    patient_conditions: Optional[list[str]] = []
    patient_allergies: Optional[list[str]] = []
    patient_blood_group: Optional[str] = None

    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    doctor_avatar: Optional[str] = None
    doctor_fee: Optional[float] = None

    model_config = {"from_attributes": True}


class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None


class TimeSlot(BaseModel):
    time: str
    available: bool
