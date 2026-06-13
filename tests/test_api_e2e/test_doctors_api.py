"""
TMS — E2E Tests: Doctor API
Tests doctor listing, specializations, schedule, earnings, profile, and medicine templates.
"""
from datetime import date


# ═══════════════════════════════════════════════
# DOCTOR LISTING (PUBLIC)
# ═══════════════════════════════════════════════

class TestDoctorListing:
    def test_list_all_doctors(self, client):
        """TC-DOC-001: List all doctors returns 6 seeded doctors."""
        resp = client.get("/api/doctors")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 6
        names = [d["name"] for d in data]
        assert "Dr. Anjali Mehta" in names
        assert "Dr. Rajesh Verma" in names

    def test_doctor_has_full_info(self, client):
        """TC-DOC-002: Doctor listing includes all required fields."""
        resp = client.get("/api/doctors")
        doc = resp.json()[0]
        required_keys = ["id", "name", "specialization", "qualification",
                         "experience", "consultation_fee", "rating", "availability_status"]
        for key in required_keys:
            assert key in doc, f"Missing key: {key}"

    def test_filter_by_specialization(self, client):
        """TC-DOC-003: Filter doctors by specialization."""
        resp = client.get("/api/doctors?specialization=Cardiology")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert all(d["specialization"] == "Cardiology" for d in data)

    def test_filter_by_availability(self, client):
        """TC-DOC-004: Filter doctors by availability status."""
        resp = client.get("/api/doctors?available=true")
        assert resp.status_code == 200
        data = resp.json()
        assert all(d["availability_status"] is True for d in data)

    def test_list_specializations(self, client):
        """TC-DOC-005: List all distinct specializations."""
        resp = client.get("/api/doctors/specializations")
        assert resp.status_code == 200
        specs = resp.json()
        assert "Cardiology" in specs
        assert "General Medicine" in specs
        assert "Pulmonology" in specs
        assert len(specs) == 6

    def test_get_single_doctor(self, client):
        """TC-DOC-006: Get a single doctor by ID."""
        resp = client.get("/api/doctors/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert data["name"] == "Dr. Anjali Mehta"
        assert data["specialization"] == "Cardiology"
        assert data["consultation_fee"] == 800

    def test_get_nonexistent_doctor(self, client):
        """TC-DOC-007: Get non-existent doctor returns 404."""
        resp = client.get("/api/doctors/999")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════
# DOCTOR SCHEDULE (REQUIRES DOCTOR AUTH)
# ═══════════════════════════════════════════════

class TestDoctorSchedule:
    def test_get_todays_schedule(self, client, doctor_headers):
        """TC-DOC-008: Doctor can view today's schedule."""
        resp = client.get("/api/doctors/schedule", headers=doctor_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # Dr. Anjali has 2 appointments seeded for today
        assert len(data) >= 1

    def test_schedule_contains_appointment_data(self, client, doctor_headers):
        """TC-DOC-009: Schedule entries contain patient and appointment info."""
        resp = client.get("/api/doctors/schedule", headers=doctor_headers)
        data = resp.json()
        if len(data) > 0:
            appt = data[0]
            assert "patient_name" in appt
            assert "start_time" in appt
            assert "status" in appt

    def test_schedule_for_specific_date(self, client, doctor_headers):
        """TC-DOC-010: Doctor can query schedule for a specific date."""
        today = date.today().isoformat()
        resp = client.get(f"/api/doctors/schedule?schedule_date={today}", headers=doctor_headers)
        assert resp.status_code == 200


# ═══════════════════════════════════════════════
# DOCTOR EARNINGS
# ═══════════════════════════════════════════════

class TestDoctorEarnings:
    def test_get_earnings_summary(self, client, doctor_headers):
        """TC-DOC-011: Doctor can view earnings summary."""
        resp = client.get("/api/doctors/earnings", headers=doctor_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_earnings" in data
        assert "daily_earnings" in data
        assert "monthly_earnings" in data
        assert "total_consultations" in data
        assert "upcoming_appointments" in data

    def test_earnings_has_total(self, client, doctor_headers):
        """TC-DOC-012: Total earnings value is non-negative."""
        resp = client.get("/api/doctors/earnings", headers=doctor_headers)
        data = resp.json()
        assert data["total_earnings"] >= 0
        assert data["total_consultations"] >= 0


# ═══════════════════════════════════════════════
# TIME SLOTS
# ═══════════════════════════════════════════════

class TestDoctorSlots:
    def test_get_available_slots(self, client):
        """TC-DOC-013: Get available time slots for a doctor on a date."""
        today = date.today().isoformat()
        resp = client.get(f"/api/doctors/1/slots?slot_date={today}")
        assert resp.status_code == 200
        slots = resp.json()
        assert isinstance(slots, list)
        assert len(slots) == 12  # 12 standard time slots
        assert all("time" in s and "available" in s for s in slots)

    def test_booked_slots_marked_unavailable(self, client):
        """TC-DOC-014: Booked slots are correctly marked as unavailable."""
        today = date.today().isoformat()
        resp = client.get(f"/api/doctors/1/slots?slot_date={today}")
        slots = resp.json()
        slot_1430 = next((s for s in slots if s["time"] == "14:30"), None)
        assert slot_1430 is not None
        # 14:30 should be booked (from seed data)
        assert slot_1430["available"] is False


# ═══════════════════════════════════════════════
# MEDICINE TEMPLATES
# ═══════════════════════════════════════════════

class TestMedicineTemplates:
    def test_list_medicine_templates(self, client, doctor_headers):
        """TC-DOC-015: Doctor can list their medicine templates."""
        resp = client.get("/api/doctors/medicines/list", headers=doctor_headers)
        assert resp.status_code == 200
        meds = resp.json()
        assert isinstance(meds, list)
        assert len(meds) >= 4  # We seeded 4 medicines per doctor

    def test_add_medicine_template(self, client, doctor_headers):
        """TC-DOC-016: Doctor can add a new medicine template."""
        resp = client.post("/api/doctors/medicines", headers=doctor_headers, json={
            "medicine_name": "Ciprofloxacin",
            "dosage_template": "Tablet 500mg",
            "instructions_template": "Take twice daily after food",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["medicine_name"] == "Ciprofloxacin"

    def test_delete_medicine_template(self, client, doctor_headers):
        """TC-DOC-017: Doctor can delete a medicine template."""
        # First add one
        add_resp = client.post("/api/doctors/medicines", headers=doctor_headers, json={
            "medicine_name": "TempMedicine",
            "dosage_template": "Temp",
            "instructions_template": "Temp",
        })
        med_id = add_resp.json()["id"]
        # Then delete it
        resp = client.delete(f"/api/doctors/medicines/{med_id}", headers=doctor_headers)
        assert resp.status_code == 200
