"""
TMS — Admin Routes
Platform analytics, doctor/patient management, monitoring.
"""
import json
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..auth.dependencies import require_admin
from ..models.user import User
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.payment import Payment
from ..schemas.doctor import DoctorUpdate
from ..services.appointment_service import build_appointment_response

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard", response_model=dict)
def admin_dashboard(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Platform overview stats."""
    total_doctors = db.query(Doctor).count()
    total_patients = db.query(Patient).count()
    total_appointments = db.query(Appointment).count()
    total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.payment_status == "success").scalar() or 0

    today = date.today()
    today_appts = db.query(Appointment).filter(Appointment.appointment_date == today).count()
    active_consultations = db.query(Appointment).filter(
        Appointment.status == "confirmed",
        Appointment.appointment_date == today,
    ).count()

    return {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "total_revenue": total_revenue,
        "today_appointments": today_appts,
        "active_consultations": active_consultations,
    }


@router.get("/analytics", response_model=dict)
def admin_analytics(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Detailed analytics: daily consultations, department load, etc."""
    today = date.today()

    # Daily consultations last 30 days
    daily = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        count = db.query(Appointment).filter(
            Appointment.appointment_date == d,
        ).count()
        daily.append({"date": d.isoformat(), "count": count})

    # Department load
    dept_load = {}
    doctors = db.query(Doctor).all()
    for doc in doctors:
        spec = doc.specialization
        if spec not in dept_load:
            dept_load[spec] = 0
        dept_load[spec] += db.query(Appointment).filter(
            Appointment.doctor_id == doc.id,
        ).count()

    # Completed this week
    week_start = today - timedelta(days=today.weekday())
    weekly_completed = db.query(Appointment).filter(
        Appointment.appointment_date >= week_start,
        Appointment.status == "completed",
    ).count()

    # New patients this week
    new_patients = db.query(Patient).filter(
        Patient.created_at >= week_start.isoformat(),
    ).count()

    return {
        "daily_consultations": daily,
        "department_load": dept_load,
        "weekly_stats": {
            "total_consultations": weekly_completed,
            "new_patients": new_patients,
            "avg_duration": "18 min",
            "satisfaction": 4.6,
        },
    }


@router.get("/doctors", response_model=list[dict])
def admin_list_doctors(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """List all doctors for admin management."""
    doctors = db.query(Doctor).all()
    return [
        {
            "id": d.id,
            "user_id": d.user_id,
            "name": d.user.name,
            "specialization": d.specialization,
            "qualification": d.qualification,
            "experience": d.experience,
            "consultation_fee": d.consultation_fee,
            "availability_status": d.availability_status,
            "rating": d.rating,
            "total_consultations": d.total_consultations,
            "avatar": "".join([w[0].upper() for w in d.user.name.split()[:2]]),
        }
        for d in doctors
    ]


@router.put("/doctors/{doctor_id}", response_model=dict)
def admin_update_doctor(
    doctor_id: int,
    data: DoctorUpdate,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin update a doctor."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)
    db.commit()
    db.refresh(doctor)
    return {"message": "Doctor updated"}


@router.get("/patients", response_model=list[dict])
def admin_list_patients(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """List all patients for admin management."""
    patients = db.query(Patient).all()
    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "name": p.user.name,
            "email": p.user.email,
            "phone": p.user.phone,
            "age": p.age,
            "gender": p.gender,
            "blood_group": p.blood_group,
            "medical_conditions": json.loads(p.medical_conditions or "[]"),
            "allergies": json.loads(p.allergies or "[]"),
            "avatar": "".join([w[0].upper() for w in p.user.name.split()[:2]]),
            "created_at": p.created_at,
        }
        for p in patients
    ]


@router.get("/appointments", response_model=list[dict])
def admin_list_appointments(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """List all appointments."""
    appts = db.query(Appointment).order_by(Appointment.appointment_date.desc()).limit(100).all()
    return [build_appointment_response(a) for a in appts]


@router.get("/payments", response_model=dict)
def admin_payments(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Revenue analytics."""
    total = db.query(func.sum(Payment.amount)).filter(Payment.payment_status == "success").scalar() or 0
    today = date.today()
    today_revenue = db.query(func.sum(Payment.amount)).join(Appointment).filter(
        Payment.payment_status == "success",
        Appointment.appointment_date == today,
    ).scalar() or 0

    month_start = today.replace(day=1)
    monthly_revenue = db.query(func.sum(Payment.amount)).join(Appointment).filter(
        Payment.payment_status == "success",
        Appointment.appointment_date >= month_start,
    ).scalar() or 0

    payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(50).all()
    return {
        "total_revenue": total,
        "today_revenue": today_revenue,
        "monthly_revenue": monthly_revenue,
        "recent_payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "payment_method": p.payment_method,
                "transaction_id": p.transaction_id,
                "payment_status": p.payment_status,
                "created_at": p.created_at,
            }
            for p in payments
        ],
    }
