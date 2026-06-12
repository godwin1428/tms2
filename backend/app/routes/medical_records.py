"""
TMS — Medical Records Routes
Upload reports/scans, list, download, delete.
"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.medical_record import MedicalRecord
from ..config import settings

from ..services.appointment_service import doctor_has_patient_access

def _verify_record_access(record: MedicalRecord, user: User, db: Session):
    if user.role == "patient" and (not user.patient_profile or record.patient_id != user.patient_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this record")
    if user.role == "doctor" and user.doctor_profile:
        if not doctor_has_patient_access(db, user.doctor_profile.id, record.patient_id):
            raise HTTPException(status_code=403, detail="Not authorized to access this record")

router = APIRouter(prefix="/api/records", tags=["Medical Records"])

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=dict)
async def upload_record(
    file: UploadFile = File(...),
    record_type: str = Form("lab"),
    description: str = Form(""),
    patient_id: int = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a medical record file."""
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed. Use: {ALLOWED_EXTENSIONS}")

    # Determine patient_id
    if user.role == "patient" and user.patient_profile:
        patient_id = user.patient_profile.id
    elif user.role == "doctor" and user.doctor_profile:
        if patient_id is None:
            raise HTTPException(status_code=400, detail="patient_id is required")
        if not doctor_has_patient_access(db, user.doctor_profile.id, patient_id):
            raise HTTPException(status_code=403, detail="Not authorized to upload for this patient")
    else:
        if patient_id is None:
            raise HTTPException(status_code=400, detail="patient_id is required")

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "records", str(patient_id))
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")

    # Magic bytes check
    header = content[:4]
    is_valid = False
    if ext in [".jpg", ".jpeg"] and header.startswith(b"\xff\xd8"):
        is_valid = True
    elif ext == ".png" and header.startswith(b"\x89PNG"):
        is_valid = True
    elif ext == ".pdf" and header.startswith(b"%PDF"):
        is_valid = True

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid file signature")

    with open(filepath, "wb") as f:
        f.write(content)

    # Save record
    doctor_id = user.doctor_profile.id if user.role == "doctor" and user.doctor_profile else None
    record = MedicalRecord(
        patient_id=patient_id,
        doctor_id=doctor_id,
        record_type=record_type,
        description=description or file.filename,
        file_path=filepath,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "record_type": record.record_type,
        "description": record.description,
        "file_path": record.file_path,
        "created_at": record.created_at,
    }


@router.get("", response_model=list[dict])
def list_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List medical records for the current user."""
    query = db.query(MedicalRecord)
    if user.role == "patient" and user.patient_profile:
        query = query.filter(MedicalRecord.patient_id == user.patient_profile.id)
    elif user.role == "doctor" and user.doctor_profile:
        from ..models.appointment import Appointment
        query = query.join(Appointment, MedicalRecord.patient_id == Appointment.patient_id)\
                     .filter(Appointment.doctor_id == user.doctor_profile.id)\
                     .distinct()
    records = query.order_by(MedicalRecord.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "patient_id": r.patient_id,
            "doctor_id": r.doctor_id,
            "record_type": r.record_type,
            "description": r.description,
            "file_path": r.file_path,
            "created_at": r.created_at,
            "doctor_name": r.doctor.user.name if r.doctor and r.doctor.user else None,
        }
        for r in records
    ]


@router.get("/{record_id}/file")
def download_file(record_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Download a record file."""
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    _verify_record_access(record, user, db)
    if not record.file_path or not os.path.exists(record.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(record.file_path)


@router.delete("/{record_id}", response_model=dict)
def delete_record(record_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a medical record."""
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    _verify_record_access(record, user, db)
    if record.file_path and os.path.exists(record.file_path):
        os.remove(record.file_path)
    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}
