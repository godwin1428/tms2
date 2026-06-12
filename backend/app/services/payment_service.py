"""
TMS — Payment Service
Mock payment gateway for UPI/Card simulation.
"""
import uuid
import random
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.payment import Payment
from ..models.appointment import Appointment


def create_payment(db: Session, appointment_id: int, method: str) -> Payment:
    """Create a mock payment and auto-verify it."""
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise ValueError("Appointment not found")

    amount = appt.doctor.consultation_fee if appt.doctor and appt.doctor.consultation_fee else 0.0

    transaction_id = f"TMS{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"

    payment = Payment(
        appointment_id=appointment_id,
        amount=amount,
        payment_method=method,
        transaction_id=transaction_id,
        payment_status="success",  # Mock: always succeeds
    )
    db.add(payment)

    # Update appointment payment status
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if appt:
        appt.payment_status = "paid"
        appt.status = "confirmed"

    db.commit()
    db.refresh(payment)
    return payment


def verify_payment(db: Session, transaction_id: str) -> dict:
    """Verify a payment by transaction ID (mock verification)."""
    payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
    if not payment:
        return {"verified": False, "message": "Transaction not found"}
    return {
        "verified": payment.payment_status == "success",
        "transaction_id": payment.transaction_id,
        "amount": payment.amount,
        "status": payment.payment_status,
    }


def get_payment_history(db: Session, user_id: int = None, limit: int = 50) -> list[Payment]:
    """Get payment history, optionally filtered by user's appointments."""
    query = db.query(Payment).order_by(Payment.created_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all()
