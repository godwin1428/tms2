"""DevicePairing model — Bluetooth wearable registration."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class DevicePairing(Base):
    __tablename__ = "device_pairings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    device_name = Column(String(100), nullable=False)
    mac_address = Column(String(17), nullable=True)
    pairing_status = Column(String(20), default="paired")  # paired, unpaired
    last_connected = Column(DateTime, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="device_pairings")
