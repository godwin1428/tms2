"""
TMS — Auth Routes
Register, Login, Refresh, Profile.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserCreate, UserLogin, TokenResponse, TokenRefresh, UserResponse, UserUpdate
from ..services.auth_service import (
    create_user, get_user_by_email, verify_password, hash_password, build_user_response,
)
from ..auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from ..auth.dependencies import get_current_user, security
from ..models.user import User, TokenBlocklist
import json

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=dict)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (patient/doctor)."""
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if data.role == "doctor":
        raise HTTPException(status_code=400, detail="Doctor registration requires admin approval")
    if data.role != "patient":
        raise HTTPException(status_code=400, detail="Invalid role.")

    user = create_user(db, data)
    user_data = build_user_response(user)

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_data,
    }


@router.post("/login", response_model=dict)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_data = build_user_response(user)
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_data,
    }


@router.post("/refresh", response_model=dict)
def refresh(data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh an access token."""
    payload = verify_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=dict)
def get_profile(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return build_user_response(user)


@router.post("/logout", response_model=dict)
def logout(
    credentials=Depends(security),
    db: Session = Depends(get_db)
):
    """Logout current user by blacklisting their token."""
    token = credentials.credentials
    if token:
        blocklist_entry = TokenBlocklist(token=token)
        db.add(blocklist_entry)
        db.commit()
    return {"message": "Successfully logged out"}


@router.put("/me", response_model=dict)
def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    if data.name:
        user.name = data.name
    if data.phone:
        user.phone = data.phone

    if user.role == "doctor" and user.doctor_profile:
        d = user.doctor_profile
        if data.specialization is not None:
            d.specialization = data.specialization
        if data.qualification is not None:
            d.qualification = data.qualification
        if data.experience is not None:
            d.experience = data.experience
        if data.consultation_fee is not None:
            d.consultation_fee = data.consultation_fee
        if data.bio is not None:
            d.bio = data.bio
        if data.availability_status is not None:
            d.availability_status = data.availability_status

    elif user.role == "patient" and user.patient_profile:
        p = user.patient_profile
        if data.age is not None:
            p.age = data.age
        if data.gender is not None:
            p.gender = data.gender
        if data.blood_group is not None:
            p.blood_group = data.blood_group
        if data.medical_conditions is not None:
            p.medical_conditions = json.dumps(data.medical_conditions)
        if data.allergies is not None:
            p.allergies = json.dumps(data.allergies)

    db.commit()
    db.refresh(user)
    return build_user_response(user)
