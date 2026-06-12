"""
TMS — Payment Routes
Create, verify, history.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.payment import Payment
from ..models.appointment import Appointment
from ..schemas.payment import PaymentCreate, PaymentVerify, PaymentResponse
from ..services.payment_service import create_payment, verify_payment

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/create", response_model=dict)
def make_payment(
    data: PaymentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create and process a payment."""
    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.role == "patient" and (not user.patient_profile or appt.patient_id != user.patient_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to pay for this appointment")
    if appt.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Already paid")

    payment = create_payment(db, data.appointment_id, data.payment_method)
    return {
        "id": payment.id,
        "appointment_id": payment.appointment_id,
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "transaction_id": payment.transaction_id,
        "payment_status": payment.payment_status,
        "created_at": payment.created_at,
    }


@router.post("/verify", response_model=dict)
def verify(data: PaymentVerify, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verify a payment by transaction ID."""
    payment_info = verify_payment(db, data.transaction_id)
    if not payment_info.get("verified"):
        return payment_info

    # Validate access
    payment_record = db.query(Payment).filter(Payment.transaction_id == data.transaction_id).first()
    if payment_record:
        appt = payment_record.appointment
        if user.role == "patient" and (not user.patient_profile or appt.patient_id != user.patient_profile.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        if user.role == "doctor" and (not user.doctor_profile or appt.doctor_id != user.doctor_profile.id):
            raise HTTPException(status_code=403, detail="Not authorized")

    return payment_info


@router.get("/history", response_model=list[dict])
def payment_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get payment history for the current user."""
    query = db.query(Payment).join(Appointment)

    if user.role == "patient" and user.patient_profile:
        query = query.filter(Appointment.patient_id == user.patient_profile.id)
    elif user.role == "doctor" and user.doctor_profile:
        query = query.filter(Appointment.doctor_id == user.doctor_profile.id)

    payments = query.order_by(Payment.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "appointment_id": p.appointment_id,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "transaction_id": p.transaction_id,
            "payment_status": p.payment_status,
            "created_at": p.created_at,
        }
        for p in payments
    ]
