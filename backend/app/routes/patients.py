"""
TMS — Patient Routes
Patient profile, medical history.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.patient import Patient
from ..models.prescription import Prescription
from ..models.medical_record import MedicalRecord
from ..models.appointment import Appointment
from ..services.prescription_service import build_prescription_response
from ..services.appointment_service import build_appointment_response, doctor_has_patient_access

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("/{patient_id}", response_model=dict)
def get_patient(patient_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get patient profile."""
    if user.role == "patient" and (not user.patient_profile or user.patient_profile.id != patient_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this patient profile")
    if user.role == "doctor" and user.doctor_profile:
        if not doctor_has_patient_access(db, user.doctor_profile.id, patient_id):
            raise HTTPException(status_code=403, detail="Not authorized to access this patient profile")
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    avatar = "".join([w[0].upper() for w in patient.user.name.split()[:2]]) if patient.user else ""
    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "name": patient.user.name,
        "email": patient.user.email,
        "phone": patient.user.phone,
        "age": patient.age,
        "gender": patient.gender,
        "blood_group": patient.blood_group,
        "medical_conditions": json.loads(patient.medical_conditions or "[]"),
        "allergies": json.loads(patient.allergies or "[]"),
        "avatar": avatar,
        "created_at": patient.created_at,
    }


@router.get("/{patient_id}/history", response_model=dict)
def get_medical_history(
    patient_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full medical history: appointments, prescriptions, records."""
    if user.role == "patient" and (not user.patient_profile or user.patient_profile.id != patient_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this patient history")
    if user.role == "doctor" and user.doctor_profile:
        if not doctor_has_patient_access(db, user.doctor_profile.id, patient_id):
            raise HTTPException(status_code=403, detail="Not authorized to access this patient history")
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.appointment_date.desc()).all()

    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id
    ).order_by(Prescription.created_at.desc()).all()

    records = db.query(MedicalRecord).filter(
        MedicalRecord.patient_id == patient_id
    ).order_by(MedicalRecord.created_at.desc()).all()

    return {
        "appointments": [build_appointment_response(a) for a in appointments],
        "prescriptions": [build_prescription_response(rx) for rx in prescriptions],
        "records": [
            {
                "id": r.id,
                "record_type": r.record_type,
                "description": r.description,
                "file_path": r.file_path,
                "created_at": r.created_at,
                "doctor_name": r.doctor.user.name if r.doctor and r.doctor.user else None,
            }
            for r in records
        ],
    }
