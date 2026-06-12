"""
TMS — Vitals Routes
Store and retrieve vitals readings (from Bluetooth sync).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/api/vitals", tags=["Vitals"])

# In-memory vitals store (for real-time; could be moved to Redis/DB later)
_vitals_store: dict[int, list[dict]] = {}


class VitalsReading(BaseModel):
    bpm: float
    spo2: float
    temperature: float
    systolic: float
    diastolic: float
    timestamp: Optional[str] = None


@router.post("/sync", response_model=dict)
def sync_vitals(data: VitalsReading, user: User = Depends(get_current_user)):
    """Store a vitals reading."""
    patient_id = user.patient_profile.id if user.patient_profile else user.id
    if patient_id not in _vitals_store:
        _vitals_store[patient_id] = []

    reading = {
        "bpm": data.bpm,
        "spo2": data.spo2,
        "temperature": data.temperature,
        "systolic": data.systolic,
        "diastolic": data.diastolic,
        "timestamp": data.timestamp or datetime.now(timezone.utc).isoformat(),
    }
    _vitals_store[patient_id].append(reading)

    # Keep last 500 readings
    if len(_vitals_store[patient_id]) > 500:
        _vitals_store[patient_id] = _vitals_store[patient_id][-500:]

    return {"message": "Vitals synced", "reading": reading}


@router.get("/history", response_model=dict)
def vitals_history(patient_id: int = None, user: User = Depends(get_current_user)):
    """Get vitals history."""
    if patient_id is None:
        patient_id = user.patient_profile.id if user.patient_profile else user.id

    readings = _vitals_store.get(patient_id, [])
    latest = readings[-1] if readings else None
    return {
        "patient_id": patient_id,
        "total_readings": len(readings),
        "latest": latest,
        "history": readings[-50:],  # Return last 50
    }
