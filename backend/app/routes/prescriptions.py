"""
TMS — Prescription Routes
Create, view, PDF download.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import os
import uuid
from ..config import settings
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.prescription import Prescription
from ..models.appointment import Appointment
from ..schemas.prescription import PrescriptionCreate
from ..services.prescription_service import create_prescription, build_prescription_response

def _verify_prescription_access(rx: Prescription, user: User):
    if user.role == "admin":
        return
    if user.role == "patient" and (not user.patient_profile or rx.patient_id != user.patient_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this prescription")
    if user.role == "doctor" and (not user.doctor_profile or rx.doctor_id != user.doctor_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this prescription")

router = APIRouter(prefix="/api/prescriptions", tags=["Prescriptions"])


@router.post("/create", response_model=dict)
def create(
    data: PrescriptionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a prescription (doctor only)."""
    if user.role != "doctor" or not user.doctor_profile:
        raise HTTPException(status_code=403, detail="Only doctors can create prescriptions")

    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appt.doctor_id != user.doctor_profile.id:
        raise HTTPException(status_code=403, detail="Not authorized for this appointment")

    rx = create_prescription(db, data, user.doctor_profile.id, appt.patient_id)

    # Generate PDF
    try:
        from ..pdf.generator import generate_prescription_pdf
        pdf_path = generate_prescription_pdf(rx, db)
        rx.pdf_path = pdf_path
        db.commit()
    except Exception as e:
        print(f"PDF generation failed: {e}")

    return build_prescription_response(rx)


@router.post("/upload-image", response_model=dict)
async def upload_prescription_image(
    appointment_id: int = Form(...),
    diagnosis: str = Form(""),
    notes: str = Form(""),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a prescription image (doctor only)."""
    if user.role != "doctor" or not user.doctor_profile:
        raise HTTPException(status_code=403, detail="Only doctors can upload prescriptions")

    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appt.doctor_id != user.doctor_profile.id:
        raise HTTPException(status_code=403, detail="Not authorized for this appointment")

    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed. Use: {allowed_exts}")

    # Ensure directories exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, "prescriptions")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    max_size = 10 * 1024 * 1024  # 10MB
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")

    # Magic bytes check
    header = content[:4]
    is_valid = False
    if ext in [".jpg", ".jpeg"] and header.startswith(b"\xff\xd8"):
        is_valid = True
    elif ext == ".png" and header.startswith(b"\x89PNG"):
        is_valid = True
    elif ext in [".webp", ".gif"]:
        is_valid = True # Skipping deep validation for these for now

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid file signature")

    with open(filepath, "wb") as f:
        f.write(content)

    # Relative static path served by app mount
    relative_path = f"/uploads/prescriptions/{filename}"

    # Create the prescription in the DB
    from ..models.doctor import Doctor

    rx = Prescription(
        appointment_id=appointment_id,
        doctor_id=user.doctor_profile.id,
        patient_id=appt.patient_id,
        diagnosis=diagnosis or "Uploaded Prescription Image",
        notes=notes,
        image_path=relative_path
    )
    db.add(rx)
    db.flush()

    # Mark appointment as completed
    appt.status = "completed"

    # Update doctor consultation count and earnings
    doctor = db.query(Doctor).filter(Doctor.id == user.doctor_profile.id).first()
    if doctor:
        doctor.total_consultations = (doctor.total_consultations or 0) + 1
        doctor.total_earnings = (doctor.total_earnings or 0) + (doctor.consultation_fee or 0)

    db.commit()
    db.refresh(rx)

    return build_prescription_response(rx)


@router.get("/{rx_id}", response_model=dict)
def get_prescription(rx_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a prescription by ID."""
    rx = db.query(Prescription).filter(Prescription.id == rx_id).first()
    if not rx:
        raise HTTPException(status_code=404, detail="Prescription not found")
    _verify_prescription_access(rx, user)
    return build_prescription_response(rx)


@router.get("/{rx_id}/pdf")
def download_pdf(rx_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Download prescription PDF."""
    rx = db.query(Prescription).filter(Prescription.id == rx_id).first()
    if not rx:
        raise HTTPException(status_code=404, detail="Prescription not found")
    _verify_prescription_access(rx, user)

    if not rx.pdf_path:
        # Generate on-the-fly
        try:
            from ..pdf.generator import generate_prescription_pdf
            pdf_path = generate_prescription_pdf(rx, db)
            rx.pdf_path = pdf_path
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    import os
    if not os.path.exists(rx.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        rx.pdf_path,
        media_type="application/pdf",
        filename=f"prescription_{rx.id}.pdf",
    )


@router.get("/patient/{patient_id}", response_model=list[dict])
def patient_prescriptions(
    patient_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all prescriptions for a patient."""
    if user.role == "patient" and (not user.patient_profile or user.patient_profile.id != patient_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this patient's prescriptions")
    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id
    ).order_by(Prescription.created_at.desc()).all()
    return [build_prescription_response(rx) for rx in prescriptions]
