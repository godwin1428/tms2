"""Appointment model — central transaction linking patient ↔ doctor."""
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    start_time = Column(String(10), nullable=False)   # "09:00"
    end_time = Column(String(10), nullable=False)      # "09:30"
    status = Column(String(20), default="pending")     # pending, confirmed, completed, cancelled
    payment_status = Column(String(20), default="pending")  # pending, paid, refunded
    meeting_room_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    payment = relationship("Payment", back_populates="appointment", uselist=False)
    prescription = relationship("Prescription", back_populates="appointment", uselist=False)
