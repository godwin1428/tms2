"""
TMS — E2E Tests: Security & Access Control
Tests authentication requirements, role-based access, and payment endpoints.
"""


class TestUnauthenticatedAccess:
    def test_me_requires_auth(self, client):
        """TC-SEC-001: /api/auth/me returns 401/403 without token."""
        resp = client.get("/api/auth/me")
        assert resp.status_code in [401, 403]

    def test_appointments_require_auth(self, client):
        """TC-SEC-002: /api/appointments requires auth."""
        resp = client.get("/api/appointments")
        assert resp.status_code in [401, 403]

    def test_admin_dashboard_requires_auth(self, client):
        """TC-SEC-003: /api/admin/dashboard requires auth."""
        resp = client.get("/api/admin/dashboard")
        assert resp.status_code in [401, 403]

    def test_doctor_schedule_requires_auth(self, client):
        """TC-SEC-004: /api/doctors/schedule requires auth."""
        resp = client.get("/api/doctors/schedule")
        assert resp.status_code in [401, 403]

    def test_doctor_earnings_requires_auth(self, client):
        """TC-SEC-005: /api/doctors/earnings requires auth."""
        resp = client.get("/api/doctors/earnings")
        assert resp.status_code in [401, 403]

    def test_prescriptions_require_auth(self, client):
        """TC-SEC-006: /api/prescriptions/{id} requires auth."""
        resp = client.get("/api/prescriptions/1")
        assert resp.status_code in [401, 403]

    def test_triage_chat_requires_auth(self, client):
        """TC-SEC-007: /api/triage/chat requires auth."""
        resp = client.post("/api/triage/chat", json={
            "message": "test",
            "conversation_history": [],
        })
        assert resp.status_code in [401, 403]

    def test_vitals_sync_requires_auth(self, client):
        """TC-SEC-008: /api/vitals/sync requires auth."""
        resp = client.post("/api/vitals/sync", json={
            "bpm": 72, "spo2": 98, "temperature": 36.6,
            "systolic": 120, "diastolic": 80,
        })
        assert resp.status_code in [401, 403]


class TestRoleBasedAccess:
    def test_patient_cannot_access_admin(self, client, patient_headers):
        """TC-SEC-009: Patient cannot access admin endpoints."""
        resp = client.get("/api/admin/dashboard", headers=patient_headers)
        assert resp.status_code == 403

    def test_doctor_cannot_access_admin(self, client, doctor_headers):
        """TC-SEC-010: Doctor cannot access admin endpoints."""
        resp = client.get("/api/admin/dashboard", headers=doctor_headers)
        assert resp.status_code == 403

    def test_patient_cannot_view_earnings(self, client, patient_headers):
        """TC-SEC-011: Patient cannot access doctor earnings."""
        resp = client.get("/api/doctors/earnings", headers=patient_headers)
        assert resp.status_code == 403

    def test_admin_can_access_all(self, client, admin_headers):
        """TC-SEC-012: Admin can access admin dashboard."""
        resp = client.get("/api/admin/dashboard", headers=admin_headers)
        assert resp.status_code == 200

    def test_invalid_token_rejected(self, client):
        """TC-SEC-013: Invalid token is rejected."""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        resp = client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 401


class TestPaymentEndpoints:
    def test_payment_history(self, client, patient_headers):
        """TC-SEC-014: Patient can view their payment history."""
        resp = client.get("/api/payments/history", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_doctor_payment_history(self, client, doctor_headers):
        """TC-SEC-015: Doctor can view their payment history."""
        resp = client.get("/api/payments/history", headers=doctor_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestVitalsEndpoints:
    def test_sync_vitals(self, client, patient_headers):
        """TC-SEC-016: Patient can sync vitals reading."""
        resp = client.post("/api/vitals/sync", headers=patient_headers, json={
            "bpm": 72.0,
            "spo2": 98.0,
            "temperature": 36.6,
            "systolic": 120.0,
            "diastolic": 80.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Vitals synced"
        assert data["reading"]["bpm"] == 72.0

    def test_vitals_history(self, client, patient_headers):
        """TC-SEC-017: Patient can view vitals history."""
        resp = client.get("/api/vitals/history", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_readings" in data
        assert "history" in data


class TestDeviceEndpoints:
    def test_pair_device(self, client, patient_headers):
        """TC-SEC-018: Patient can pair a Bluetooth device."""
        resp = client.post("/api/devices/pair", headers=patient_headers, json={
            "device_name": "Pulse Oximeter X1",
            "mac_address": "AA:BB:CC:DD:EE:FF",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["device_name"] == "Pulse Oximeter X1"
        assert data["pairing_status"] == "paired"

    def test_list_devices(self, client, patient_headers):
        """TC-SEC-019: Patient can list paired devices."""
        resp = client.get("/api/devices", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_unpair_device(self, client, patient_headers):
        """TC-SEC-020: Patient can unpair a device."""
        # First pair a device
        pair_resp = client.post("/api/devices/pair", headers=patient_headers, json={
            "device_name": "Temp Device",
            "mac_address": "11:22:33:44:55:66",
        })
        device_id = pair_resp.json()["id"]

        # Then unpair it
        resp = client.delete(f"/api/devices/{device_id}", headers=patient_headers)
        assert resp.status_code == 200


class TestPublicEndpoints:
    def test_doctors_list_is_public(self, client):
        """TC-SEC-021: Doctor listing is publicly accessible."""
        resp = client.get("/api/doctors")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_specializations_is_public(self, client):
        """TC-SEC-022: Specializations list is publicly accessible."""
        resp = client.get("/api/doctors/specializations")
        assert resp.status_code == 200

    def test_triage_status_is_public(self, client):
        """TC-SEC-023: Triage status is publicly accessible."""
        resp = client.get("/api/triage/status")
        assert resp.status_code == 200

    def test_health_is_public(self, client):
        """TC-SEC-024: Health endpoint is publicly accessible."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
