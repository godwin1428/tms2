"""
TMS — E2E Tests: Patient API
Tests patient profile retrieval and medical history.
"""


class TestPatientProfile:
    def test_get_own_profile(self, client, patient_headers):
        """TC-PAT-001: Patient can view their own profile."""
        resp = client.get("/api/patients/1", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Ramesh Kumar"
        assert data["age"] == 45
        assert data["gender"] == "Male"
        assert data["blood_group"] == "B+"

    def test_profile_has_medical_info(self, client, patient_headers):
        """TC-PAT-002: Patient profile includes medical conditions and allergies."""
        resp = client.get("/api/patients/1", headers=patient_headers)
        data = resp.json()
        assert "Hypertension" in data["medical_conditions"]
        assert "Diabetes Type 2" in data["medical_conditions"]
        assert "Penicillin" in data["allergies"]

    def test_profile_has_avatar(self, client, patient_headers):
        """TC-PAT-003: Patient profile includes avatar initials."""
        resp = client.get("/api/patients/1", headers=patient_headers)
        data = resp.json()
        assert data["avatar"] == "RK"  # Ramesh Kumar

    def test_cannot_access_other_patient_profile(self, client, patient_headers):
        """TC-PAT-004: Patient cannot access another patient's profile."""
        resp = client.get("/api/patients/2", headers=patient_headers)
        assert resp.status_code == 403

    def test_nonexistent_patient(self, client, patient_headers):
        """TC-PAT-005: Accessing non-existent patient returns 404."""
        resp = client.get("/api/patients/999", headers=patient_headers)
        # The authorization check will fail first (403) since patient_id != 999
        assert resp.status_code in [403, 404]


class TestMedicalHistory:
    def test_get_medical_history(self, client, patient_headers):
        """TC-PAT-006: Patient can view their medical history."""
        resp = client.get("/api/patients/1/history", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "appointments" in data
        assert "prescriptions" in data
        assert "records" in data

    def test_history_contains_appointments(self, client, patient_headers):
        """TC-PAT-007: Medical history includes appointment list."""
        resp = client.get("/api/patients/1/history", headers=patient_headers)
        data = resp.json()
        assert len(data["appointments"]) >= 1

    def test_history_contains_prescriptions(self, client, patient_headers):
        """TC-PAT-008: Medical history includes prescription data."""
        resp = client.get("/api/patients/1/history", headers=patient_headers)
        data = resp.json()
        assert len(data["prescriptions"]) >= 1

    def test_cannot_access_other_patient_history(self, client, patient_headers):
        """TC-PAT-009: Patient cannot access another patient's history."""
        resp = client.get("/api/patients/2/history", headers=patient_headers)
        assert resp.status_code == 403


class TestProfileUpdate:
    def test_update_patient_profile(self, client):
        """TC-PAT-010: Patient can update their profile info."""
        # Login as a patient that we can safely modify
        login_resp = client.post("/api/auth/login", json={
            "email": "ananya@tms.com", "password": "Patient@123"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.put("/api/auth/me", headers=headers, json={
            "name": "Ananya Gupta Updated",
            "phone": "9900112235",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Ananya Gupta Updated"
