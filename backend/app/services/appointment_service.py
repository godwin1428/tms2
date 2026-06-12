"""
TMS — Appointment Service
Slot management, double-booking prevention, room access validation.
"""
import uuid
import json
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..models.appointment import Appointment
from ..models.doctor import Doctor

# Standard 30-min time slots
ALL_SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
]


def get_available_slots(db: Session, doctor_id: int, appt_date: date) -> list[dict]:
    """Return all slots with availability status for a given doctor and date."""
    booked = db.query(Appointment.start_time).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appt_date,
        Appointment.status.in_(["pending", "confirmed"]),
    ).all()
    booked_times = {b[0] for b in booked}

    return [
        {"time": slot, "available": slot not in booked_times}
        for slot in ALL_SLOTS
    ]


def check_slot_available(db: Session, doctor_id: int, appt_date: date, start_time: str) -> bool:
    """Check if a specific slot is available."""
    existing = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appt_date,
        Appointment.start_time == start_time,
        Appointment.status.in_(["pending", "confirmed"]),
    ).first()
    return existing is None


def calculate_end_time(start_time: str) -> str:
    """Add 30 minutes to start_time."""
    h, m = map(int, start_time.split(":"))
    total = h * 60 + m + 30
    return f"{total // 60:02d}:{total % 60:02d}"


def generate_room_id() -> str:
    """Generate a unique meeting room ID."""
    return f"room_{uuid.uuid4().hex[:12]}"


def check_room_access(appointment: Appointment) -> dict:
    """Check if the consultation room should be accessible (5-min window before start)."""
    now = datetime.now(timezone.utc)
    appt_dt = datetime.combine(
        appointment.appointment_date,
        datetime.strptime(appointment.start_time, "%H:%M").time(),
    ).replace(tzinfo=timezone.utc)
    
    window_start = appt_dt - timedelta(minutes=5)
    end_dt = datetime.combine(
        appointment.appointment_date,
        datetime.strptime(appointment.end_time, "%H:%M").time(),
    ).replace(tzinfo=timezone.utc)

    is_accessible = window_start <= now <= end_dt
    return {
        "accessible": is_accessible or appointment.status == "confirmed",
        "starts_at": appt_dt.isoformat(),
        "window_opens": window_start.isoformat(),
        "room_id": appointment.meeting_room_id,
    }


def build_appointment_response(appt: Appointment) -> dict:
    """Build a rich appointment response with joined patient/doctor data."""
    patient = appt.patient
    doctor = appt.doctor
    patient_user = patient.user if patient else None
    doctor_user = doctor.user if doctor else None

    return {
        "id": appt.id,
        "patient_id": appt.patient_id,
        "doctor_id": appt.doctor_id,
        "appointment_date": appt.appointment_date,
        "start_time": appt.start_time,
        "end_time": appt.end_time,
        "status": appt.status,
        "payment_status": appt.payment_status,
        "meeting_room_id": appt.meeting_room_id,
        "created_at": appt.created_at,
        "patient_name": patient_user.name if patient_user else None,
        "patient_age": patient.age if patient else None,
        "patient_gender": patient.gender if patient else None,
        "patient_avatar": "".join([w[0].upper() for w in patient_user.name.split()[:2]]) if patient_user else None,
        "patient_conditions": json.loads(patient.medical_conditions or "[]") if patient else [],
        "patient_allergies": json.loads(patient.allergies or "[]") if patient else [],
        "patient_blood_group": patient.blood_group if patient else None,
        "doctor_name": doctor_user.name if doctor_user else None,
        "doctor_specialization": doctor.specialization if doctor else None,
        "doctor_avatar": "".join([w[0].upper() for w in doctor_user.name.split()[:2]]) if doctor_user else None,
        "doctor_fee": doctor.consultation_fee if doctor else None,
        "prescription_id": appt.prescription.id if appt.prescription else None,
    }

def doctor_has_patient_access(db: Session, doctor_id: int, patient_id: int) -> bool:
    """Check if a doctor has an appointment with the given patient."""
    count = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.patient_id == patient_id
    ).count()
    return count > 0

