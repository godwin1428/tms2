"""Device Pairing schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DevicePairCreate(BaseModel):
    device_name: str
    mac_address: Optional[str] = None


class DevicePairResponse(BaseModel):
    id: int
    patient_id: int
    device_name: str
    mac_address: Optional[str] = None
    pairing_status: str
    last_connected: Optional[datetime] = None

    model_config = {"from_attributes": True}
