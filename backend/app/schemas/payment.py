"""Payment schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    appointment_id: int
    amount: float
    payment_method: str = "UPI"  # UPI, Card, NetBanking


class PaymentVerify(BaseModel):
    transaction_id: str


class PaymentResponse(BaseModel):
    id: int
    appointment_id: int
    amount: float
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_status: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
