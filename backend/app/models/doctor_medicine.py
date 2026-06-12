"""DoctorMedicine model — per-doctor medicine templates."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class DoctorMedicine(Base):
    __tablename__ = "doctor_medicines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    medicine_name = Column(String(100), nullable=False)
    dosage_template = Column(String(50), nullable=True)
    instructions_template = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    doctor = relationship("Doctor", back_populates="medicines")
