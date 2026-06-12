"""Doctor model — profile linked to User."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String(100), nullable=False)
    qualification = Column(String(200), nullable=True)
    experience = Column(Integer, default=0)
    consultation_fee = Column(Float, default=500.0)
    profile_image = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    availability_status = Column(Boolean, default=True)
    total_earnings = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    total_consultations = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor")
    medicines = relationship("DoctorMedicine", back_populates="doctor", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="doctor")
    medical_records = relationship("MedicalRecord", back_populates="doctor")
