"""
TMS — SQLAlchemy Models
Exports all models for easy import.
"""
from .user import User, TokenBlocklist
from .doctor import Doctor
from .patient import Patient
from .appointment import Appointment
from .payment import Payment
from .prescription import Prescription, PrescriptionMedicine
from .doctor_medicine import DoctorMedicine
from .medical_record import MedicalRecord
from .device_pairing import DevicePairing

__all__ = [
    "User",
    "Doctor",
    "Patient",
    "Appointment",
    "Payment",
    "Prescription",
    "PrescriptionMedicine",
    "DoctorMedicine",
    "MedicalRecord",
    "DevicePairing",
    "TokenBlocklist",
]
