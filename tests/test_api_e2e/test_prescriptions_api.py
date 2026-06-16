"""
TMS — E2E Tests: Prescription API
Tests prescription listing, retrieval, creation, and patient-specific queries.
"""


class TestPrescriptionRetrieval:
    def test_get_prescription_by_id(self, client, patient_headers):
        """TC-RX-001: Patient can get their own prescription by ID."""
        resp = client.get("/api/prescriptions/1", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert data["diagnosis"] == "Essential Hypertension - Stage 1"
        assert data["patient_id"] == 1

    def test_prescription_has_medicines(self, client, patient_headers):
        """TC-RX-002: Prescription includes medicine list."""
        resp = client.get("/api/prescriptions/1", headers=patient_headers)
        data = resp.json()
        assert "medicines" in data
        assert len(data["medicines"]) == 2
        medicine_names = [m["medicine_name"] for m in data["medicines"]]
        assert "Amlodipine" in medicine_names
        assert "Metformin" in medicine_names

    def test_prescription_has_doctor_info(self, client, patient_headers):
        """TC-RX-003: Prescription includes doctor info."""
        resp = client.get("/api/prescriptions/1", headers=patient_headers)
        data = resp.json()
        assert data["doctor_name"] == "Dr. Anjali Mehta"
        assert data["doctor_specialization"] == "Cardiology"

    def test_prescription_has_patient_info(self, client, patient_headers):
        """TC-RX-004: Prescription includes patient info."""
        resp = client.get("/api/prescriptions/1", headers=patient_headers)
        data = resp.json()
        assert data["patient_name"] == "Ramesh Kumar"

    def test_get_nonexistent_prescription(self, client, patient_headers):
        """TC-RX-005: Non-existent prescription returns 404."""
        resp = client.get("/api/prescriptions/999", headers=patient_headers)
        assert resp.status_code == 404


class TestPatientPrescriptions:
    def test_list_patient_prescriptions(self, client, patient_headers):
        """TC-RX-006: Patient can list their prescriptions."""
        resp = client.get("/api/prescriptions/patient/1", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_cannot_access_other_patient_prescriptions(self, client, patient_headers):
        """TC-RX-007: Patient cannot access another patient's prescriptions."""
        resp = client.get("/api/prescriptions/patient/2", headers=patient_headers)
        assert resp.status_code == 403


class TestPrescriptionCreation:
    def test_doctor_create_prescription(self, client, doctor_headers):
        """TC-RX-008: Doctor can create a prescription for their appointment."""
        # Appointment 6 is Dr. Anjali + Lakshmi (we completed it earlier)
        resp = client.post("/api/prescriptions/create", headers=doctor_headers, json={
            "appointment_id": 6,
            "diagnosis": "Common Cold",
            "notes": "Rest and hydration recommended.",
            "medicines": [
                {
                    "medicine_name": "Paracetamol",
                    "dosage": "650mg",
                    "frequency": "Thrice daily",
                    "duration": "3 days",
                    "instructions": "After food",
                },
            ],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["diagnosis"] == "Common Cold"
        assert len(data["medicines"]) == 1

    def test_patient_cannot_create_prescription(self, client, patient_headers):
        """TC-RX-009: Patient cannot create a prescription."""
        resp = client.post("/api/prescriptions/create", headers=patient_headers, json={
            "appointment_id": 1,
            "diagnosis": "Test",
            "medicines": [],
        })
        assert resp.status_code == 403
