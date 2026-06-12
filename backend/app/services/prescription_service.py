"""
TMS — Prescription Service
Create prescriptions and link medicines.
"""
import json
from sqlalchemy.orm import Session
from ..models.prescription import Prescription, PrescriptionMedicine
from ..models.appointment import Appointment
from ..models.doctor import Doctor
from ..schemas.prescription import PrescriptionCreate


def create_prescription(
    db: Session,
    data: PrescriptionCreate,
    doctor_id: int,
    patient_id: int,
) -> Prescription:
    """Create a prescription with medicines."""
    prescription = Prescription(
        appointment_id=data.appointment_id,
        doctor_id=doctor_id,
        patient_id=patient_id,
        diagnosis=data.diagnosis,
        notes=data.notes,
    )
    db.add(prescription)
    db.flush()

    for med in data.medicines:
        pm = PrescriptionMedicine(
            prescription_id=prescription.id,
            medicine_name=med.medicine_name,
            dosage=med.dosage,
            frequency=med.frequency,
            duration=med.duration,
            instructions=med.instructions,
        )
        db.add(pm)

    # Mark appointment as completed
    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if appt:
        appt.status = "completed"

    # Update doctor consultation count and earnings
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor:
        doctor.total_consultations = (doctor.total_consultations or 0) + 1
        doctor.total_earnings = (doctor.total_earnings or 0) + (doctor.consultation_fee or 0)

    db.commit()
    db.refresh(prescription)
    return prescription


def build_prescription_response(rx: Prescription) -> dict:
    """Build a rich prescription response."""
    doctor_user = rx.doctor.user if rx.doctor else None
    patient_user = rx.patient.user if rx.patient else None
    return {
        "id": rx.id,
        "appointment_id": rx.appointment_id,
        "doctor_id": rx.doctor_id,
        "patient_id": rx.patient_id,
        "diagnosis": rx.diagnosis,
        "notes": rx.notes,
        "pdf_path": rx.pdf_path,
        "image_path": rx.image_path,
        "created_at": rx.created_at,
        "doctor_name": doctor_user.name if doctor_user else None,
        "doctor_specialization": rx.doctor.specialization if rx.doctor else None,
        "patient_name": patient_user.name if patient_user else None,
        "patient_age": rx.patient.age if rx.patient else None,
        "patient_gender": rx.patient.gender if rx.patient else None,
        "medicines": [
            {
                "id": m.id,
                "medicine_name": m.medicine_name,
                "dosage": m.dosage,
                "frequency": m.frequency,
                "duration": m.duration,
                "instructions": m.instructions,
            }
            for m in rx.medicines
        ],
    }
