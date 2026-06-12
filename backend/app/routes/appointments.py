"""
TMS — Appointment Routes
Book, list, update, cancel, room access check.
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.appointment import Appointment
from ..models.doctor import Doctor
from ..schemas.appointment import AppointmentCreate, AppointmentUpdate
from ..services.appointment_service import (
    check_slot_available, calculate_end_time, generate_room_id,
    build_appointment_response, check_room_access,
)

def _verify_appt_access(appt: Appointment, user: User):
    if user.role == "admin":
        return
    if user.role == "patient" and (not user.patient_profile or appt.patient_id != user.patient_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this appointment")
    if user.role == "doctor" and (not user.doctor_profile or appt.doctor_id != user.doctor_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this appointment")

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.post("/book", response_model=dict)
def book_appointment(
    data: AppointmentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Book an appointment (patient only)."""
    if user.role != "patient" or not user.patient_profile:
        raise HTTPException(status_code=403, detail="Only patients can book appointments")

    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor.availability_status:
        raise HTTPException(status_code=400, detail="Doctor is currently offline")

    if not check_slot_available(db, data.doctor_id, data.appointment_date, data.start_time):
        raise HTTPException(status_code=409, detail="Slot already booked")

    end_time = data.end_time or calculate_end_time(data.start_time)

    appointment = Appointment(
        patient_id=user.patient_profile.id,
        doctor_id=data.doctor_id,
        appointment_date=data.appointment_date,
        start_time=data.start_time,
        end_time=end_time,
        status="pending",
        payment_status="pending",
        meeting_room_id=generate_room_id(),
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return build_appointment_response(appointment)


@router.get("", response_model=list[dict])
def list_appointments(
    status_filter: str = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List appointments for the current user."""
    query = db.query(Appointment)

    if user.role == "patient" and user.patient_profile:
        query = query.filter(Appointment.patient_id == user.patient_profile.id)
    elif user.role == "doctor" and user.doctor_profile:
        query = query.filter(Appointment.doctor_id == user.doctor_profile.id)
    # admin sees all

    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.start_time).all()
    return [build_appointment_response(a) for a in appointments]


@router.get("/{appt_id}", response_model=dict)
def get_appointment(
    appt_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single appointment."""
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    _verify_appt_access(appt, user)
    return build_appointment_response(appt)


@router.put("/{appt_id}", response_model=dict)
def update_appointment(
    appt_id: int,
    data: AppointmentUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update appointment status."""
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    _verify_appt_access(appt, user)

    if data.status:
        if user.role == "patient" and data.status != "cancelled":
            raise HTTPException(status_code=403, detail="Patients can only cancel appointments")
        if user.role == "doctor" and data.status not in ("cancelled", "completed"):
            raise HTTPException(status_code=403, detail="Doctors can only complete or cancel appointments")
        appt.status = data.status
    if data.payment_status:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Cannot update payment status manually")
        appt.payment_status = data.payment_status

    db.commit()
    db.refresh(appt)
    return build_appointment_response(appt)


@router.delete("/{appt_id}", response_model=dict)
def cancel_appointment(
    appt_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel an appointment."""
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    _verify_appt_access(appt, user)
    appt.status = "cancelled"
    db.commit()
    return {"message": "Appointment cancelled"}


@router.get("/{appt_id}/room-access", response_model=dict)
def get_room_access(
    appt_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if consultation room is accessible (5-min pre-window)."""
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    _verify_appt_access(appt, user)
    return check_room_access(appt)
