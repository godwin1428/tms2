"""
TMS — E2E Tests: Appointment API
Tests appointment listing, booking, status updates, cancellation, and room access.
"""
from datetime import date, timedelta


class TestAppointmentListing:
    def test_patient_list_appointments(self, client, patient_headers):
        """TC-APT-001: Patient can list their appointments."""
        resp = client.get("/api/appointments", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_appointment_has_full_info(self, client, patient_headers):
        """TC-APT-002: Appointment response includes doctor and patient info."""
        resp = client.get("/api/appointments", headers=patient_headers)
        data = resp.json()
        appt = data[0]
        assert "doctor_name" in appt
        assert "patient_name" in appt
        assert "status" in appt
        assert "appointment_date" in appt
        assert "start_time" in appt

    def test_doctor_list_appointments(self, client, doctor_headers):
        """TC-APT-003: Doctor can list their appointments."""
        resp = client.get("/api/appointments", headers=doctor_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_filter_by_status(self, client, patient_headers):
        """TC-APT-004: Appointments can be filtered by status."""
        resp = client.get("/api/appointments?status_filter=completed", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        if len(data) > 0:
            assert all(a["status"] == "completed" for a in data)

    def test_get_single_appointment(self, client, patient_headers):
        """TC-APT-005: Patient can get a single appointment by ID."""
        resp = client.get("/api/appointments/1", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1


class TestAppointmentBooking:
    def test_book_appointment(self, client):
        """TC-APT-006: Patient can book a new appointment."""
        # Login as a patient
        login_resp = client.post("/api/auth/login", json={
            "email": "arjun@tms.com", "password": "Patient@123"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        resp = client.post("/api/appointments/book", headers=headers, json={
            "doctor_id": 1,
            "appointment_date": tomorrow,
            "start_time": "11:00",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending"
        assert data["doctor_id"] == 1
        assert data["start_time"] == "11:00"
        assert data["meeting_room_id"] is not None

    def test_double_booking_blocked(self, client):
        """TC-APT-007: Double-booking the same slot is blocked."""
        login_resp = client.post("/api/auth/login", json={
            "email": "priya@tms.com", "password": "Patient@123"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        resp = client.post("/api/appointments/book", headers=headers, json={
            "doctor_id": 1,
            "appointment_date": tomorrow,
            "start_time": "11:00",  # Same slot as above
        })
        assert resp.status_code == 409

    def test_book_with_nonexistent_doctor(self, client, patient_headers):
        """TC-APT-008: Booking with non-existent doctor returns 404."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        resp = client.post("/api/appointments/book", headers=patient_headers, json={
            "doctor_id": 999,
            "appointment_date": tomorrow,
            "start_time": "09:00",
        })
        assert resp.status_code == 404


class TestAppointmentUpdates:
    def test_patient_cancel_appointment(self, client):
        """TC-APT-009: Patient can cancel their appointment."""
        # Login as Mohammed who has a pending appointment (ID=5)
        login_resp = client.post("/api/auth/login", json={
            "email": "mohammed@tms.com", "password": "Patient@123"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.put("/api/appointments/5", headers=headers, json={
            "status": "cancelled"
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_doctor_complete_appointment(self, client, doctor_headers):
        """TC-APT-010: Doctor can mark an appointment as completed."""
        # Dr. Anjali (doctor_headers) has appointment with Lakshmi (ID=6)
        resp = client.put("/api/appointments/6", headers=doctor_headers, json={
            "status": "completed"
        })
        assert resp.status_code == 200

    def test_get_room_access(self, client, patient_headers):
        """TC-APT-011: Room access check returns access info."""
        resp = client.get("/api/appointments/1/room-access", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "accessible" in data
        assert "room_id" in data
