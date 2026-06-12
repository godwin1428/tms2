"""
TMS — Database Seed Script
Populate database with initial data matching the existing frontend MockData.
"""
import json
import sys
import os

# Add parent directory to path so we can import the app
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.prescription import Prescription, PrescriptionMedicine
from app.models.doctor_medicine import DoctorMedicine
from app.models.medical_record import MedicalRecord
from app.services.auth_service import hash_password
from datetime import date, datetime, timezone


def seed_database():
    """Seed the database with initial data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ═══════════════════════════════════════
        # 1. Admin User
        # ═══════════════════════════════════════
        admin = User(name="Admin User", email="admin@tms.com", phone="9000000000",
                     password_hash=hash_password("Admin@123"), role="admin")
        db.add(admin)
        db.flush()

        # ═══════════════════════════════════════
        # 2. Doctors
        # ═══════════════════════════════════════
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

        # ═══════════════════════════════════════
        # 3. Patients
        # ═══════════════════════════════════════
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
        for pd in patients_data:
            user = User(name=pd["name"], email=pd["email"], phone=pd["phone"],
                        password_hash=hash_password("Patient@123"), role="patient")
            db.add(user)
            db.flush()
            pat = Patient(
                user_id=user.id, age=pd["age"], gender=pd["gender"],
                blood_group=pd["blood"],
                medical_conditions=json.dumps(pd["conditions"]),
                allergies=json.dumps(pd["allergies"]),
            )
            db.add(pat)
            db.flush()
            patient_objs.append(pat)

        # ═══════════════════════════════════════
        # 4. Doctor Medicine Templates
        # ═══════════════════════════════════════
        medicines = [
            ("Amoxicillin", "Capsule 500mg", "Take after meals"),
            ("Metformin", "Tablet 500mg", "Take with food"),
            ("Amlodipine", "Tablet 5mg", "Take in the morning"),
            ("Atorvastatin", "Tablet 20mg", "Take at bedtime"),
            ("Omeprazole", "Capsule 20mg", "Take before breakfast"),
            ("Paracetamol", "Tablet 650mg", "As needed for fever/pain"),
            ("Cetirizine", "Tablet 10mg", "Take at bedtime"),
            ("Salbutamol", "Inhaler 100mcg", "2 puffs as needed"),
            ("Losartan", "Tablet 50mg", "Take once daily"),
            ("Montelukast", "Tablet 10mg", "Take at bedtime"),
            ("Pantoprazole", "Tablet 40mg", "Take before meals"),
            ("Azithromycin", "Tablet 500mg", "Take for 3 days"),
            ("Clopidogrel", "Tablet 75mg", "Take once daily"),
            ("Levothyroxine", "Tablet 50mcg", "Take empty stomach"),
            ("Ibuprofen", "Tablet 400mg", "Take after food, max 3 per day"),
        ]

        for doc in doctor_objs:
            for name, dosage, instructions in medicines:
                dm = DoctorMedicine(
                    doctor_id=doc.id,
                    medicine_name=name,
                    dosage_template=dosage,
                    instructions_template=instructions,
                )
                db.add(dm)

        # ═══════════════════════════════════════
        # 5. Sample Appointments
        # ═══════════════════════════════════════
        today = date.today()
        appts_data = [
            {"patient": 0, "doctor": 0, "date": today, "time": "09:00", "status": "completed", "pay": "paid"},
            {"patient": 1, "doctor": 2, "date": today, "time": "09:30", "status": "completed", "pay": "paid"},
            {"patient": 2, "doctor": 1, "date": today, "time": "10:00", "status": "confirmed", "pay": "paid"},
            {"patient": 3, "doctor": 3, "date": today, "time": "10:30", "status": "confirmed", "pay": "paid"},
            {"patient": 4, "doctor": 1, "date": today, "time": "14:00", "status": "pending", "pay": "pending"},
            {"patient": 5, "doctor": 0, "date": today, "time": "14:30", "status": "pending", "pay": "pending"},
        ]

        appt_objs = []
        for ad in appts_data:
            h, m = map(int, ad["time"].split(":"))
            end_time = f"{h:02d}:{m + 30:02d}" if m + 30 < 60 else f"{h + 1:02d}:{(m + 30) % 60:02d}"
            appt = Appointment(
                patient_id=patient_objs[ad["patient"]].id,
                doctor_id=doctor_objs[ad["doctor"]].id,
                appointment_date=ad["date"],
                start_time=ad["time"],
                end_time=end_time,
                status=ad["status"],
                payment_status=ad["pay"],
                meeting_room_id=f"room_{ad['patient']}_{ad['doctor']}_{ad['time'].replace(':', '')}",
            )
            db.add(appt)
            db.flush()
            appt_objs.append(appt)

            # Create payments for paid appointments
            if ad["pay"] == "paid":
                payment = Payment(
                    appointment_id=appt.id,
                    amount=doctor_objs[ad["doctor"]].consultation_fee,
                    payment_method="UPI",
                    transaction_id=f"TMS{today.strftime('%Y%m%d')}{appt.id:04d}",
                    payment_status="success",
                )
                db.add(payment)

        # ═══════════════════════════════════════
        # 6. Sample Prescriptions (for completed appointments)
        # ═══════════════════════════════════════
        # Prescription 1: Ramesh Kumar → Dr. Anjali Mehta
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

        # Prescription 2: Sunita Devi → Dr. Suresh Iyer
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
        print("[Seed] Seeded: 1 admin, 6 doctors, 8 patients, 90 medicines, 6 appointments, 2 prescriptions")

    except Exception as e:
        db.rollback()
        print(f"[Seed] Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
