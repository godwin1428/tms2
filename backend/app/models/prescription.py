"""Prescription + PrescriptionMedicine models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    diagnosis = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    pdf_path = Column(String(255), nullable=True)
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    appointment = relationship("Appointment", back_populates="prescription")
    doctor = relationship("Doctor", back_populates="prescriptions")
    patient = relationship("Patient", back_populates="prescriptions")
    medicines = relationship("PrescriptionMedicine", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionMedicine(Base):
    __tablename__ = "prescription_medicines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    medicine_name = Column(String(100), nullable=False)
    dosage = Column(String(50), nullable=True)
    frequency = Column(String(50), nullable=True)
    duration = Column(String(30), nullable=True)
    instructions = Column(Text, nullable=True)

    # Relationships
    prescription = relationship("Prescription", back_populates="medicines")
