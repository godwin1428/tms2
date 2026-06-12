"""
TMS — Device Pairing Routes
Register, list, update, unpair Bluetooth devices.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user, require_patient
from ..models.user import User
from ..models.device_pairing import DevicePairing
from ..schemas.device_pairing import DevicePairCreate, DevicePairResponse

router = APIRouter(prefix="/api/devices", tags=["Devices"])


@router.post("/pair", response_model=DevicePairResponse)
def pair_device(
    data: DevicePairCreate,
    user: User = Depends(require_patient),
    db: Session = Depends(get_db),
):
    """Register a Bluetooth device."""
    patient = user.patient_profile
    device = DevicePairing(
        patient_id=patient.id,
        device_name=data.device_name,
        mac_address=data.mac_address,
        pairing_status="paired",
        last_connected=datetime.now(timezone.utc),
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("", response_model=list[DevicePairResponse])
def list_devices(user: User = Depends(require_patient), db: Session = Depends(get_db)):
    """List paired devices."""
    return db.query(DevicePairing).filter(
        DevicePairing.patient_id == user.patient_profile.id
    ).all()


@router.put("/{device_id}", response_model=dict)
def update_device(
    device_id: int,
    user: User = Depends(require_patient),
    db: Session = Depends(get_db),
):
    """Update device connection timestamp."""
    device = db.query(DevicePairing).filter(
        DevicePairing.id == device_id,
        DevicePairing.patient_id == user.patient_profile.id,
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.last_connected = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Device updated"}


@router.delete("/{device_id}", response_model=dict)
def unpair_device(
    device_id: int,
    user: User = Depends(require_patient),
    db: Session = Depends(get_db),
):
    """Unpair a device."""
    device = db.query(DevicePairing).filter(
        DevicePairing.id == device_id,
        DevicePairing.patient_id == user.patient_profile.id,
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
    return {"message": "Device unpaired"}
