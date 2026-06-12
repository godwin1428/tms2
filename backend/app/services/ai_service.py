"""
TMS — AI Service (Stub)
Simulated AI features — swap with real API integrations later.
"""
import random


def analyze_symptoms(symptoms: list[str]) -> dict:
    """Stub AI symptom analyzer. Returns simulated analysis."""
    conditions = {
        "fever": ["Viral Infection", "Malaria", "Dengue", "COVID-19"],
        "headache": ["Migraine", "Tension Headache", "Sinusitis"],
        "cough": ["Bronchitis", "Asthma", "Pneumonia", "Common Cold"],
        "chest pain": ["Angina", "GERD", "Costochondritis"],
        "fatigue": ["Anemia", "Hypothyroidism", "Diabetes"],
        "shortness of breath": ["Asthma", "COPD", "Heart Failure"],
    }

    possible = []
    for symptom in symptoms:
        key = symptom.lower().strip()
        for k, v in conditions.items():
            if k in key:
                possible.extend(v)

    if not possible:
        possible = ["General Consultation Recommended"]

    unique = list(set(possible))[:5]
    return {
        "symptoms": symptoms,
        "possible_conditions": unique,
        "severity": random.choice(["Low", "Moderate", "High"]),
        "recommendation": "Please consult a doctor for proper diagnosis.",
        "disclaimer": "This is an AI-generated analysis and should not be used as a substitute for professional medical advice.",
    }


def generate_medical_summary(patient_data: dict) -> str:
    """Stub AI medical summary generator."""
    name = patient_data.get("name", "Patient")
    conditions = patient_data.get("conditions", [])
    age = patient_data.get("age", "N/A")

    summary = f"Patient {name}, aged {age}."
    if conditions:
        summary += f" Known conditions: {', '.join(conditions)}."
    summary += " Regular follow-up recommended. Maintain prescribed medication schedule."
    return summary


def suggest_prescription(diagnosis: str) -> list[dict]:
    """Stub AI prescription assistant."""
    templates = {
        "hypertension": [
            {"medicine_name": "Amlodipine", "dosage": "Tablet 5mg", "frequency": "Once daily", "duration": "30 days"},
            {"medicine_name": "Losartan", "dosage": "Tablet 50mg", "frequency": "Once daily", "duration": "30 days"},
        ],
        "diabetes": [
            {"medicine_name": "Metformin", "dosage": "Tablet 500mg", "frequency": "Twice daily", "duration": "30 days"},
        ],
        "infection": [
            {"medicine_name": "Amoxicillin", "dosage": "Capsule 500mg", "frequency": "Thrice daily", "duration": "7 days"},
            {"medicine_name": "Paracetamol", "dosage": "Tablet 650mg", "frequency": "As needed", "duration": "5 days"},
        ],
    }

    diagnosis_lower = diagnosis.lower()
    for key, meds in templates.items():
        if key in diagnosis_lower:
            return meds

    return [{"medicine_name": "Paracetamol", "dosage": "Tablet 500mg", "frequency": "As needed", "duration": "5 days"}]
