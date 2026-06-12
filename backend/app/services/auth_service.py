"""
TMS — Auth Service
Password hashing, user creation, login validation.
"""
import json
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, data: UserCreate) -> User:
    """Create a user and the corresponding role-specific profile."""
    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.flush()  # get user.id before creating profile

    if data.role == "doctor":
        doctor = Doctor(
            user_id=user.id,
            specialization=data.specialization or "General Medicine",
            qualification=data.qualification or "",
            experience=data.experience or 0,
            consultation_fee=data.consultation_fee or 500.0,
            bio=data.bio or "",
            availability_status=True,
        )
        db.add(doctor)
    elif data.role == "patient":
        patient = Patient(
            user_id=user.id,
            age=data.age,
            gender=data.gender,
            blood_group=data.blood_group,
            medical_conditions=json.dumps(data.medical_conditions or []),
            allergies=json.dumps(data.allergies or []),
        )
        db.add(patient)

    db.commit()
    db.refresh(user)
    return user


def build_user_response(user: User) -> dict:
    """Build a full user response dict with profile data."""
    avatar = "".join([w[0].upper() for w in user.name.split()[:2]]) if user.name else "U"
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "created_at": user.created_at,
        "avatar": avatar,
        "doctor_id": None,
        "patient_id": None,
    }

    if user.role == "doctor" and user.doctor_profile:
        d = user.doctor_profile
        data.update({
            "doctor_id": d.id,
            "specialization": d.specialization,
            "qualification": d.qualification,
            "experience": d.experience,
            "consultation_fee": d.consultation_fee,
            "bio": d.bio,
            "availability_status": d.availability_status,
            "total_earnings": d.total_earnings,
            "rating": d.rating,
            "total_consultations": d.total_consultations,
        })
    elif user.role == "patient" and user.patient_profile:
        p = user.patient_profile
        data.update({
            "patient_id": p.id,
            "age": p.age,
            "gender": p.gender,
            "blood_group": p.blood_group,
            "medical_conditions": json.loads(p.medical_conditions or "[]"),
            "allergies": json.loads(p.allergies or "[]"),
        })

    return data
