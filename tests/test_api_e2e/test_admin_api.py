"""
TMS — E2E Tests: Admin API
Tests admin dashboard, analytics, doctor/patient management, and payments.
"""


class TestAdminDashboard:
    def test_dashboard_returns_stats(self, client, admin_headers):
        """TC-ADM-001: Admin dashboard returns platform statistics."""
        resp = client.get("/api/admin/dashboard", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_doctors" in data
        assert "total_patients" in data
        assert "total_appointments" in data
        assert "total_revenue" in data
        assert "today_appointments" in data

    def test_dashboard_doctor_count(self, client, admin_headers):
        """TC-ADM-002: Dashboard shows correct doctor count."""
        resp = client.get("/api/admin/dashboard", headers=admin_headers)
        data = resp.json()
        assert data["total_doctors"] == 6

    def test_dashboard_patient_count(self, client, admin_headers):
        """TC-ADM-003: Dashboard shows correct patient count."""
        resp = client.get("/api/admin/dashboard", headers=admin_headers)
        data = resp.json()
        # 8 seeded + 1 registered in test_auth_api = 9
        assert data["total_patients"] >= 8

    def test_dashboard_revenue_positive(self, client, admin_headers):
        """TC-ADM-004: Dashboard total revenue is non-negative."""
        resp = client.get("/api/admin/dashboard", headers=admin_headers)
        data = resp.json()
        assert data["total_revenue"] >= 0

    def test_dashboard_today_appointments(self, client, admin_headers):
        """TC-ADM-005: Dashboard shows today's appointment count."""
        resp = client.get("/api/admin/dashboard", headers=admin_headers)
        data = resp.json()
        assert data["today_appointments"] >= 0

    def test_non_admin_cannot_access_dashboard(self, client, patient_headers):
        """TC-ADM-006: Non-admin users cannot access admin dashboard."""
        resp = client.get("/api/admin/dashboard", headers=patient_headers)
        assert resp.status_code == 403


class TestAdminAnalytics:
    def test_analytics_returns_data(self, client, admin_headers):
        """TC-ADM-007: Analytics endpoint returns detailed metrics."""
        resp = client.get("/api/admin/analytics", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "daily_consultations" in data
        assert "department_load" in data
        assert "weekly_stats" in data

    def test_analytics_daily_consultations(self, client, admin_headers):
        """TC-ADM-008: Daily consultations has 30 days of data."""
        resp = client.get("/api/admin/analytics", headers=admin_headers)
        data = resp.json()
        assert len(data["daily_consultations"]) == 30
        day = data["daily_consultations"][0]
        assert "date" in day
        assert "count" in day

    def test_analytics_department_load(self, client, admin_headers):
        """TC-ADM-009: Department load has specialization data."""
        resp = client.get("/api/admin/analytics", headers=admin_headers)
        data = resp.json()
        assert isinstance(data["department_load"], dict)
        assert "Cardiology" in data["department_load"]


class TestAdminDoctorManagement:
    def test_list_all_doctors(self, client, admin_headers):
        """TC-ADM-010: Admin can list all doctors."""
        resp = client.get("/api/admin/doctors", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 6
        names = [d["name"] for d in data]
        assert "Dr. Anjali Mehta" in names
        assert "Dr. Rajesh Verma" in names

    def test_doctor_entry_has_details(self, client, admin_headers):
        """TC-ADM-011: Doctor entries have specialization and rating."""
        resp = client.get("/api/admin/doctors", headers=admin_headers)
        doc = resp.json()[0]
        assert "specialization" in doc
        assert "rating" in doc
        assert "total_consultations" in doc


class TestAdminPatientManagement:
    def test_list_all_patients(self, client, admin_headers):
        """TC-ADM-012: Admin can list all patients."""
        resp = client.get("/api/admin/patients", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 8
        names = [p["name"] for p in data]
        assert "Ramesh Kumar" in names
        assert "Sunita Devi" in names

    def test_patient_entry_has_medical_data(self, client, admin_headers):
        """TC-ADM-013: Patient entries include medical conditions."""
        resp = client.get("/api/admin/patients", headers=admin_headers)
        patient = next(p for p in resp.json() if p["name"] == "Ramesh Kumar")
        assert "Hypertension" in patient["medical_conditions"]


class TestAdminAppointments:
    def test_list_all_appointments(self, client, admin_headers):
        """TC-ADM-014: Admin can list all appointments."""
        resp = client.get("/api/admin/appointments", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestAdminPayments:
    def test_payment_analytics(self, client, admin_headers):
        """TC-ADM-015: Admin can view payment analytics."""
        resp = client.get("/api/admin/payments", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_revenue" in data
        assert "today_revenue" in data
        assert "monthly_revenue" in data
        assert "recent_payments" in data
        assert isinstance(data["recent_payments"], list)
