"""Payment model — financial transaction per appointment."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(20), nullable=True)   # UPI, Card, NetBanking
    transaction_id = Column(String(100), unique=True, nullable=True)
    payment_status = Column(String(20), default="pending")  # pending, success, failed, refunded
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    appointment = relationship("Appointment", back_populates="payment")
