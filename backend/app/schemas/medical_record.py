"""Medical Record schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: Optional[int] = None
    record_type: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    doctor_name: Optional[str] = None

    model_config = {"from_attributes": True}
