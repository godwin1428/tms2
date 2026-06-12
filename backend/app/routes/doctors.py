"""
TMS — Doctor Routes
Doctor profiles, schedules, earnings, medicine templates.
"""
import json
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user, require_doctor
from ..models.user import User
from ..models.doctor import Doctor
from ..models.doctor_medicine import DoctorMedicine
from ..models.appointment import Appointment
from ..models.payment import Payment
from ..schemas.doctor import (
    DoctorResponse, DoctorUpdate, DoctorEarnings,
    DoctorMedicineCreate, DoctorMedicineResponse, DoctorMedicineUpdate,
)
from ..services.appointment_service import build_appointment_response

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])


@router.get("", response_model=list[dict])
def list_doctors(
    specialization: str = Query(None),
    available: bool = Query(None),
    db: Session = Depends(get_db),
):
    """List all doctors with optional filters."""
    query = db.query(Doctor)
    if specialization:
        query = query.filter(Doctor.specialization == specialization)
    if available is not None:
        query = query.filter(Doctor.availability_status == available)

    doctors = query.all()
    result = []
    for d in doctors:
        avatar = "".join([w[0].upper() for w in d.user.name.split()[:2]]) if d.user else ""
        result.append({
            "id": d.id,
            "user_id": d.user_id,
            "name": d.user.name,
            "email": d.user.email,
            "specialization": d.specialization,
            "qualification": d.qualification,
            "experience": d.experience,
            "consultation_fee": d.consultation_fee,
            "bio": d.bio,
            "availability_status": d.availability_status,
            "rating": d.rating,
            "total_consultations": d.total_consultations,
            "avatar": avatar,
        })
    return result


@router.get("/specializations", response_model=list[str])
def list_specializations(db: Session = Depends(get_db)):
    """List all distinct specializations."""
    specs = db.query(Doctor.specialization).distinct().all()
    return [s[0] for s in specs if s[0]]


@router.get("/schedule", response_model=list[dict])
def get_schedule(
    schedule_date: date = Query(None),
    user: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    """Get doctor's appointments for a date (defaults to today)."""
    if schedule_date is None:
        schedule_date = date.today()

    doctor = user.doctor_profile
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == schedule_date,
    ).order_by(Appointment.start_time).all()

    return [build_appointment_response(a) for a in appointments]


@router.get("/earnings", response_model=dict)
def get_earnings(user: User = Depends(require_doctor), db: Session = Depends(get_db)):
    """Get doctor's earnings summary."""
    doctor = user.doctor_profile
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    today = date.today()

    # Daily earnings
    daily_appts = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == today,
        Appointment.status == "completed",
    ).all()
    daily_earnings = sum(doctor.consultation_fee for _ in daily_appts)

    # Monthly earnings
    month_start = today.replace(day=1)
    monthly_appts = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= month_start,
        Appointment.status == "completed",
    ).all()
    monthly_earnings = sum(doctor.consultation_fee for _ in monthly_appts)

    # Upcoming
    upcoming = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status.in_(["pending", "confirmed"]),
        Appointment.appointment_date >= today,
    ).count()

    return {
        "total_earnings": doctor.total_earnings,
        "daily_earnings": daily_earnings,
        "monthly_earnings": monthly_earnings,
        "total_consultations": doctor.total_consultations,
        "upcoming_appointments": upcoming,
    }


@router.get("/{doctor_id}", response_model=dict)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get a single doctor profile."""
    d = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    avatar = "".join([w[0].upper() for w in d.user.name.split()[:2]]) if d.user else ""
    return {
        "id": d.id, "user_id": d.user_id, "name": d.user.name, "email": d.user.email,
        "specialization": d.specialization, "qualification": d.qualification,
        "experience": d.experience, "consultation_fee": d.consultation_fee,
        "bio": d.bio, "availability_status": d.availability_status,
        "rating": d.rating, "total_consultations": d.total_consultations,
        "avatar": avatar,
    }


@router.get("/{doctor_id}/slots", response_model=list[dict])
def get_doctor_slots(
    doctor_id: int,
    slot_date: date = Query(...),
    db: Session = Depends(get_db),
):
    """Get available time slots for a doctor on a specific date."""
    from ..services.appointment_service import get_available_slots
    return get_available_slots(db, doctor_id, slot_date)


@router.put("/{doctor_id}", response_model=dict)
def update_doctor(
    doctor_id: int,
    data: DoctorUpdate,
    user: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    """Update doctor profile (own profile only)."""
    doctor = user.doctor_profile
    if not doctor or doctor.id != doctor_id:
        raise HTTPException(status_code=403, detail="Can only update own profile")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)
    return {"message": "Profile updated"}


# ── Medicine Templates ──

@router.get("/medicines/list", response_model=list[DoctorMedicineResponse])
def list_medicines(user: User = Depends(require_doctor), db: Session = Depends(get_db)):
    """List doctor's medicine templates."""
    doctor = user.doctor_profile
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return db.query(DoctorMedicine).filter(DoctorMedicine.doctor_id == doctor.id).all()


@router.post("/medicines", response_model=DoctorMedicineResponse)
def add_medicine(
    data: DoctorMedicineCreate,
    user: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    """Add a medicine template."""
    doctor = user.doctor_profile
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    med = DoctorMedicine(
        doctor_id=doctor.id,
        medicine_name=data.medicine_name,
        dosage_template=data.dosage_template,
        instructions_template=data.instructions_template,
    )
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


@router.put("/medicines/{med_id}", response_model=dict)
def update_medicine(
    med_id: int,
    data: DoctorMedicineUpdate,
    user: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    """Update a medicine template."""
    doctor = user.doctor_profile
    med = db.query(DoctorMedicine).filter(
        DoctorMedicine.id == med_id, DoctorMedicine.doctor_id == doctor.id,
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(med, field, value)
    db.commit()
    return {"message": "Medicine updated"}


@router.delete("/medicines/{med_id}", response_model=dict)
def delete_medicine(
    med_id: int,
    user: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    """Delete a medicine template."""
    doctor = user.doctor_profile
    med = db.query(DoctorMedicine).filter(
        DoctorMedicine.id == med_id, DoctorMedicine.doctor_id == doctor.id,
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(med)
    db.commit()
    return {"message": "Medicine deleted"}
