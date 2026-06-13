"""
TMS — API E2E Test Configuration
Fixtures for FastAPI TestClient, database seeding, and Excel report generation.
Uses an in-memory SQLite database for isolation and speed.
"""
import os
import sys
import json
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure the backend directory is on the Python path
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
sys.path.insert(0, BACKEND_DIR)

# Set env vars BEFORE importing the app (so config picks them up)
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_ci_e2e_tests_2026")
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.prescription import Prescription, PrescriptionMedicine
from app.models.doctor_medicine import DoctorMedicine
from app.services.auth_service import hash_password

# ── Globals for test result collection ──
test_results = []
suite_start_time = None


# ── In-memory test engine ──
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    """Override FastAPI's DB dependency with the test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Database seeding ──
def seed_test_database():
    """Seed the test database with data matching the production seed_data.py."""
    db = TestSessionLocal()
    try:
        # 1. Admin
        admin = User(name="Admin User", email="admin@tms.com", phone="9000000000",
                     password_hash=hash_password("Admin@123"), role="admin")
        db.add(admin)
        db.flush()

        # 2. Doctors
        doctors_data = [
            {"name": "Dr. Anjali Mehta", "email": "anjali@tms.com", "phone": "9100000001",
             "spec": "Cardiology", "qual": "MD, DM Cardiology", "exp": 12, "fee": 800, "rating": 4.8, "consults": 1847},
            {"name": "Dr. Rajesh Verma", "email": "rajesh@tms.com", "phone": "9100000002",
             "spec": "General Medicine", "qual": "MBBS, MD Medicine", "exp": 8, "fee": 500, "rating": 4.6, "consults": 2341},
            {"name": "Dr. Suresh Iyer", "email": "suresh@tms.com", "phone": "9100000003",
             "spec": "Pulmonology", "qual": "MD, DM Pulmonology", "exp": 15, "fee": 900, "rating": 4.9, "consults": 3102},
            {"name": "Dr. Kavita Nair", "email": "kavita@tms.com", "phone": "9100000004",
             "spec": "Dermatology", "qual": "MD Dermatology", "exp": 6, "fee": 600, "rating": 4.5, "consults": 1203},
            {"name": "Dr. Amit Shah", "email": "amit@tms.com", "phone": "9100000005",
             "spec": "Orthopedics", "qual": "MS Orthopedics", "exp": 10, "fee": 700, "rating": 4.7, "consults": 1590},
            {"name": "Dr. Neha Reddy", "email": "neha@tms.com", "phone": "9100000006",
             "spec": "Pediatrics", "qual": "MD Pediatrics", "exp": 9, "fee": 550, "rating": 4.8, "consults": 2089},
        ]

        doctor_objs = []
        for dd in doctors_data:
            user = User(name=dd["name"], email=dd["email"], phone=dd["phone"],
                        password_hash=hash_password("Doctor@123"), role="doctor")
            db.add(user)
            db.flush()
            doc = Doctor(
                user_id=user.id, specialization=dd["spec"], qualification=dd["qual"],
                experience=dd["exp"], consultation_fee=dd["fee"],
                availability_status=True, rating=dd["rating"],
                total_consultations=dd["consults"],
                total_earnings=dd["consults"] * dd["fee"],
                bio=f"Experienced {dd['spec']} specialist with {dd['exp']} years of practice.",
            )
            db.add(doc)
            db.flush()
            doctor_objs.append(doc)

        # 3. Patients
        patients_data = [
            {"name": "Ramesh Kumar", "email": "ramesh@tms.com", "phone": "9876543210",
             "age": 45, "gender": "Male", "blood": "B+",
             "conditions": ["Hypertension", "Diabetes Type 2"], "allergies": ["Penicillin"]},
            {"name": "Sunita Devi", "email": "sunita@tms.com", "phone": "9123456780",
             "age": 38, "gender": "Female", "blood": "O+",
             "conditions": ["Asthma"], "allergies": []},
            {"name": "Arjun Singh", "email": "arjun@tms.com", "phone": "9988776655",
             "age": 62, "gender": "Male", "blood": "A+",
             "conditions": ["Arthritis", "High Cholesterol"], "allergies": ["Sulfa"]},
            {"name": "Priya Sharma", "email": "priya@tms.com", "phone": "9112233445",
             "age": 29, "gender": "Female", "blood": "AB-",
             "conditions": [], "allergies": ["Aspirin"]},
            {"name": "Mohammed Ali", "email": "mohammed@tms.com", "phone": "9334455667",
             "age": 55, "gender": "Male", "blood": "O-",
             "conditions": ["COPD", "Diabetes Type 1"], "allergies": []},
            {"name": "Lakshmi Rao", "email": "lakshmi@tms.com", "phone": "9556677889",
             "age": 42, "gender": "Female", "blood": "B-",
             "conditions": ["Thyroid"], "allergies": ["Latex"]},
            {"name": "Vikram Patel", "email": "vikram@tms.com", "phone": "9778899001",
             "age": 33, "gender": "Male", "blood": "A-",
             "conditions": [], "allergies": []},
            {"name": "Ananya Gupta", "email": "ananya@tms.com", "phone": "9900112234",
             "age": 27, "gender": "Female", "blood": "AB+",
             "conditions": ["Migraine"], "allergies": ["Ibuprofen"]},
        ]

        patient_objs = []
        for pd_item in patients_data:
            user = User(name=pd_item["name"], email=pd_item["email"], phone=pd_item["phone"],
                        password_hash=hash_password("Patient@123"), role="patient")
            db.add(user)
            db.flush()
            pat = Patient(
                user_id=user.id, age=pd_item["age"], gender=pd_item["gender"],
                blood_group=pd_item["blood"],
                medical_conditions=json.dumps(pd_item["conditions"]),
                allergies=json.dumps(pd_item["allergies"]),
            )
            db.add(pat)
            db.flush()
            patient_objs.append(pat)

        # 4. Medicine templates for first doctor
        medicines = [
            ("Amoxicillin", "Capsule 500mg", "Take after meals"),
            ("Metformin", "Tablet 500mg", "Take with food"),
            ("Amlodipine", "Tablet 5mg", "Take in the morning"),
            ("Paracetamol", "Tablet 650mg", "As needed for fever/pain"),
        ]
        for doc in doctor_objs[:2]:
            for name, dosage, instructions in medicines:
                dm = DoctorMedicine(
                    doctor_id=doc.id,
                    medicine_name=name,
                    dosage_template=dosage,
                    instructions_template=instructions,
                )
                db.add(dm)

        # 5. Appointments
        today = date.today()
        appts_data = [
            {"patient": 0, "doctor": 0, "time": "09:00", "status": "completed", "pay": "paid"},
            {"patient": 1, "doctor": 2, "time": "09:30", "status": "completed", "pay": "paid"},
            {"patient": 2, "doctor": 1, "time": "10:00", "status": "confirmed", "pay": "paid"},
            {"patient": 3, "doctor": 3, "time": "10:30", "status": "confirmed", "pay": "paid"},
            {"patient": 4, "doctor": 1, "time": "14:00", "status": "pending", "pay": "pending"},
            {"patient": 5, "doctor": 0, "time": "14:30", "status": "pending", "pay": "pending"},
        ]

        appt_objs = []
        for ad in appts_data:
            h, m = map(int, ad["time"].split(":"))
            end_time = f"{h:02d}:{m + 30:02d}" if m + 30 < 60 else f"{h + 1:02d}:{(m + 30) % 60:02d}"
            appt = Appointment(
                patient_id=patient_objs[ad["patient"]].id,
                doctor_id=doctor_objs[ad["doctor"]].id,
                appointment_date=today,
                start_time=ad["time"],
                end_time=end_time,
                status=ad["status"],
                payment_status=ad["pay"],
                meeting_room_id=f"room_{ad['patient']}_{ad['doctor']}_{ad['time'].replace(':', '')}",
            )
            db.add(appt)
            db.flush()
            appt_objs.append(appt)

            if ad["pay"] == "paid":
                payment = Payment(
                    appointment_id=appt.id,
                    amount=doctor_objs[ad["doctor"]].consultation_fee,
                    payment_method="UPI",
                    transaction_id=f"TMS{today.strftime('%Y%m%d')}{appt.id:04d}",
                    payment_status="success",
                )
                db.add(payment)

        # 6. Prescriptions
        rx1 = Prescription(
            appointment_id=appt_objs[0].id,
            doctor_id=doctor_objs[0].id,
            patient_id=patient_objs[0].id,
            diagnosis="Essential Hypertension - Stage 1",
            notes="BP elevated. Increased Amlodipine dosage. Follow up in 2 weeks.",
        )
        db.add(rx1)
        db.flush()
        for med_data in [
            ("Amlodipine", "Tablet 5mg", "Once daily", "30 days", "Take in the morning"),
            ("Metformin", "Tablet 500mg", "Twice daily", "30 days", "After meals"),
        ]:
            db.add(PrescriptionMedicine(
                prescription_id=rx1.id,
                medicine_name=med_data[0], dosage=med_data[1],
                frequency=med_data[2], duration=med_data[3], instructions=med_data[4],
            ))

        rx2 = Prescription(
            appointment_id=appt_objs[1].id,
            doctor_id=doctor_objs[2].id,
            patient_id=patient_objs[1].id,
            diagnosis="Acute Bronchitis",
            notes="Prescribed bronchodilator + 5-day antibiotics course.",
        )
        db.add(rx2)
        db.flush()
        for med_data in [
            ("Salbutamol", "Inhaler 100mcg", "As needed", "30 days", "2 puffs when breathless"),
            ("Azithromycin", "Tablet 500mg", "Once daily", "5 days", "Take after food"),
        ]:
            db.add(PrescriptionMedicine(
                prescription_id=rx2.id,
                medicine_name=med_data[0], dosage=med_data[1],
                frequency=med_data[2], duration=med_data[3], instructions=med_data[4],
            ))

        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


# ── Pytest hooks for Excel report ──
def pytest_configure(config):
    global suite_start_time
    suite_start_time = datetime.now()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        module_name = os.path.basename(item.module.__file__).replace("test_", "").replace(".py", "")
        category_map = {
            "health": "Health & Backend",
            "auth_api": "Authentication",
            "doctors_api": "Doctor Management",
            "patients_api": "Patient Management",
            "appointments_api": "Appointment Management",
            "prescriptions_api": "Prescriptions",
            "admin_api": "Admin Dashboard",
            "triage_api": "AI Triage",
            "security_api": "Security & Access Control",
        }
        category = category_map.get(module_name, module_name.replace("_", " ").title())
        test_results.append({
            "No.": len(test_results) + 1,
            "Category": category,
            "Test Name": item.name,
            "Status": "Passed" if report.passed else "Failed",
            "Error Details": str(report.longrepr)[:500] if report.failed else "",
        })


def pytest_sessionfinish(session, exitstatus):
    try:
        import pandas as pd
    except ImportError:
        print("\n[Report] pandas not installed, skipping Excel report generation.")
        return

    end_time = datetime.now()
    duration = (end_time - suite_start_time).total_seconds()
    passed_count = sum(1 for t in test_results if t["Status"] == "Passed")
    failed_count = sum(1 for t in test_results if t["Status"] == "Failed")
    total_count = len(test_results)
    pass_rate = round((passed_count / total_count * 100), 2) if total_count > 0 else 0

    summary_data = [{
        "Test Suite": "TMS API E2E Tests",
        "Total Tests": total_count,
        "Passed": passed_count,
        "Failed": failed_count,
        "Pass Rate %": pass_rate,
        "Duration (sec)": round(duration, 2),
        "Start Time": suite_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
    }]

    details_df = pd.DataFrame(test_results)
    if details_df.empty:
        details_df = pd.DataFrame(columns=["No.", "Category", "Test Name", "Status", "Error Details"])

    passed_df = details_df[details_df["Status"] == "Passed"].copy() if not details_df.empty else pd.DataFrame()
    failed_df = details_df[details_df["Status"] == "Failed"].copy() if not details_df.empty else pd.DataFrame()

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        f"E2E_Test_Report_TMS_{timestamp}.xlsx",
    )

    try:
        import openpyxl
        with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
            passed_df.to_excel(writer, sheet_name="Passed Tests", index=False)
            failed_df.to_excel(writer, sheet_name="Failed Tests", index=False)
            details_df.to_excel(writer, sheet_name="Execution Log", index=False)
            details_df.to_excel(writer, sheet_name="Test Details", index=False)

        print(f"\n{'='*60}")
        print(f"  EXCEL TEST REPORT: {report_path}")
        print(f"  Total: {total_count}  |  Passed: {passed_count}  |  Failed: {failed_count}  |  Rate: {pass_rate}%")
        print(f"{'='*60}")
    except Exception as e:
        print(f"\n[Report] Excel generation failed: {e}")
        # Print summary to console as fallback
        print(f"\n{'='*60}")
        print(f"  TEST SUMMARY (console)")
        print(f"  Total: {total_count}  |  Passed: {passed_count}  |  Failed: {failed_count}  |  Rate: {pass_rate}%")
        print(f"{'='*60}")


# ── Fixtures ──

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables and seed the test database once per session."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    seed_test_database()
    app.dependency_overrides[get_db] = override_get_db

    # Increase rate limit for tests (default 100 req/60s is too low for 120+ tests)
    from app.main import RateLimitingMiddleware
    for middleware in app.user_middleware:
        if middleware.cls == RateLimitingMiddleware:
            break
    # Clear any existing rate limit state by patching the middleware instances
    for route in app.routes:
        pass
    # Directly patch the middleware's rate_limit on the app's middleware stack
    for m in app.middleware_stack.__dict__.get("app", app).__dict__.values():
        if isinstance(m, RateLimitingMiddleware):
            m.rate_limit = 10000
            break
    # Alternative: patch all RateLimitingMiddleware instances in the ASGI stack
    _patch_rate_limit(app.middleware_stack, 10000)

    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=TEST_ENGINE)


def _patch_rate_limit(obj, new_limit):
    """Recursively walk the ASGI middleware stack to find and patch RateLimitingMiddleware."""
    from app.main import RateLimitingMiddleware
    if isinstance(obj, RateLimitingMiddleware):
        obj.rate_limit = new_limit
        return
    # Walk the .app attribute chain
    inner = getattr(obj, "app", None)
    if inner is not None and inner is not obj:
        _patch_rate_limit(inner, new_limit)


@pytest.fixture(scope="session")
def client():
    """Provide a FastAPI TestClient for the session."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def admin_token(client):
    """Login as admin and return the access token."""
    resp = client.post("/api/auth/login", json={"email": "admin@tms.com", "password": "Admin@123"})
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    """Return auth headers for admin."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def doctor_token(client):
    """Login as Dr. Anjali and return the access token."""
    resp = client.post("/api/auth/login", json={"email": "anjali@tms.com", "password": "Doctor@123"})
    assert resp.status_code == 200, f"Doctor login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def doctor_headers(doctor_token):
    """Return auth headers for doctor."""
    return {"Authorization": f"Bearer {doctor_token}"}


@pytest.fixture(scope="session")
def patient_token(client):
    """Login as Ramesh and return the access token."""
    resp = client.post("/api/auth/login", json={"email": "ramesh@tms.com", "password": "Patient@123"})
    assert resp.status_code == 200, f"Patient login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def patient_headers(patient_token):
    """Return auth headers for patient."""
    return {"Authorization": f"Bearer {patient_token}"}
