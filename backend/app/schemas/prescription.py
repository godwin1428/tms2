"""Prescription schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PrescriptionMedicineCreate(BaseModel):
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None


class PrescriptionMedicineResponse(BaseModel):
    id: int
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None

    model_config = {"from_attributes": True}


class PrescriptionCreate(BaseModel):
    appointment_id: int
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    medicines: list[PrescriptionMedicineCreate] = []


class PrescriptionResponse(BaseModel):
    id: int
    appointment_id: int
    doctor_id: int
    patient_id: int
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    pdf_path: Optional[str] = None
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None
    medicines: list[PrescriptionMedicineResponse] = []

    # Joined
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None

    model_config = {"from_attributes": True}
