"""
TMS — E2E Tests: Authentication & Authorization
Tests login, registration, token refresh, profile, logout, and error cases.
"""
import uuid


# ═══════════════════════════════════════════════
# LOGIN TESTS
# ═══════════════════════════════════════════════

class TestAdminLogin:
    def test_admin_login_success(self, client):
        """TC-AUTH-001: Admin can login with valid credentials."""
        resp = client.post("/api/auth/login", json={"email": "admin@tms.com", "password": "Admin@123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["role"] == "admin"
        assert data["user"]["email"] == "admin@tms.com"

    def test_admin_login_wrong_password(self, client):
        """TC-AUTH-002: Admin login fails with wrong password."""
        resp = client.post("/api/auth/login", json={"email": "admin@tms.com", "password": "WrongPassword"})
        assert resp.status_code == 401

    def test_admin_login_empty_password(self, client):
        """TC-AUTH-003: Admin login fails with empty password."""
        resp = client.post("/api/auth/login", json={"email": "admin@tms.com", "password": ""})
        assert resp.status_code == 401


class TestDoctorLogin:
    def test_doctor_login_success(self, client):
        """TC-AUTH-004: Doctor can login with valid credentials."""
        resp = client.post("/api/auth/login", json={"email": "anjali@tms.com", "password": "Doctor@123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["role"] == "doctor"
        assert data["user"]["name"] == "Dr. Anjali Mehta"
        assert data["user"]["doctor_id"] is not None

    def test_doctor_login_wrong_password(self, client):
        """TC-AUTH-005: Doctor login fails with wrong password."""
        resp = client.post("/api/auth/login", json={"email": "anjali@tms.com", "password": "wrong"})
        assert resp.status_code == 401

    def test_second_doctor_login(self, client):
        """TC-AUTH-006: Second doctor (Rajesh) can login."""
        resp = client.post("/api/auth/login", json={"email": "rajesh@tms.com", "password": "Doctor@123"})
        assert resp.status_code == 200
        assert resp.json()["user"]["name"] == "Dr. Rajesh Verma"

    def test_third_doctor_login(self, client):
        """TC-AUTH-007: Third doctor (Suresh) can login."""
        resp = client.post("/api/auth/login", json={"email": "suresh@tms.com", "password": "Doctor@123"})
        assert resp.status_code == 200

    def test_fourth_doctor_login(self, client):
        """TC-AUTH-008: Fourth doctor (Kavita) can login."""
        resp = client.post("/api/auth/login", json={"email": "kavita@tms.com", "password": "Doctor@123"})
        assert resp.status_code == 200

    def test_fifth_doctor_login(self, client):
        """TC-AUTH-009: Fifth doctor (Amit) can login."""
        resp = client.post("/api/auth/login", json={"email": "amit@tms.com", "password": "Doctor@123"})
        assert resp.status_code == 200

    def test_sixth_doctor_login(self, client):
        """TC-AUTH-010: Sixth doctor (Neha) can login."""
        resp = client.post("/api/auth/login", json={"email": "neha@tms.com", "password": "Doctor@123"})
        assert resp.status_code == 200


class TestPatientLogin:
    def test_patient_login_success(self, client):
        """TC-AUTH-011: Patient can login with valid credentials."""
        resp = client.post("/api/auth/login", json={"email": "ramesh@tms.com", "password": "Patient@123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["role"] == "patient"
        assert data["user"]["name"] == "Ramesh Kumar"
        assert data["user"]["patient_id"] is not None

    def test_patient_login_wrong_password(self, client):
        """TC-AUTH-012: Patient login fails with wrong password."""
        resp = client.post("/api/auth/login", json={"email": "ramesh@tms.com", "password": "bad"})
        assert resp.status_code == 401

    def test_second_patient_login(self, client):
        """TC-AUTH-013: Second patient (Sunita) can login."""
        resp = client.post("/api/auth/login", json={"email": "sunita@tms.com", "password": "Patient@123"})
        assert resp.status_code == 200
        assert resp.json()["user"]["name"] == "Sunita Devi"

    def test_third_patient_login(self, client):
        """TC-AUTH-014: Third patient (Arjun) can login."""
        resp = client.post("/api/auth/login", json={"email": "arjun@tms.com", "password": "Patient@123"})
        assert resp.status_code == 200

    def test_fourth_patient_login(self, client):
        """TC-AUTH-015: Fourth patient (Priya) can login."""
        resp = client.post("/api/auth/login", json={"email": "priya@tms.com", "password": "Patient@123"})
        assert resp.status_code == 200

    def test_fifth_patient_login(self, client):
        """TC-AUTH-016: Fifth patient (Mohammed) can login."""
        resp = client.post("/api/auth/login", json={"email": "mohammed@tms.com", "password": "Patient@123"})
        assert resp.status_code == 200

    def test_sixth_patient_login(self, client):
        """TC-AUTH-017: Sixth patient (Lakshmi) can login."""
        resp = client.post("/api/auth/login", json={"email": "lakshmi@tms.com", "password": "Patient@123"})
        assert resp.status_code == 200


class TestInvalidLogin:
    def test_nonexistent_email(self, client):
        """TC-AUTH-018: Login fails with non-existent email."""
        resp = client.post("/api/auth/login", json={"email": "nobody@nowhere.com", "password": "password123"})
        assert resp.status_code == 401

    def test_empty_email(self, client):
        """TC-AUTH-019: Login fails with empty email."""
        resp = client.post("/api/auth/login", json={"email": "", "password": "password"})
        assert resp.status_code == 401

    def test_empty_both_fields(self, client):
        """TC-AUTH-020: Login fails with both fields empty."""
        resp = client.post("/api/auth/login", json={"email": "", "password": ""})
        assert resp.status_code == 401

    def test_sql_injection_attempt(self, client):
        """TC-AUTH-021: Login is safe from SQL injection."""
        resp = client.post("/api/auth/login", json={"email": "' OR 1=1 --", "password": "' OR 1=1 --"})
        assert resp.status_code == 401

    def test_xss_attempt_in_email(self, client):
        """TC-AUTH-022: Login is safe from XSS in email field."""
        resp = client.post("/api/auth/login", json={"email": "<script>alert('xss')</script>", "password": "password"})
        assert resp.status_code == 401


# ═══════════════════════════════════════════════
# REGISTRATION TESTS
# ═══════════════════════════════════════════════

class TestRegistration:
    def test_patient_registration_success(self, client):
        """TC-AUTH-023: New patient can register successfully."""
        uid = uuid.uuid4().hex[:6]
        resp = client.post("/api/auth/register", json={
            "name": f"Test Patient {uid}",
            "email": f"testpat_{uid}@test.com",
            "phone": "9999900001",
            "password": "Test@123",
            "role": "patient",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["role"] == "patient"

    def test_duplicate_email_registration(self, client):
        """TC-AUTH-024: Registration fails with duplicate email."""
        resp = client.post("/api/auth/register", json={
            "name": "Duplicate User",
            "email": "ramesh@tms.com",
            "phone": "9999900002",
            "password": "Test@123",
            "role": "patient",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_doctor_registration_blocked(self, client):
        """TC-AUTH-025: Doctor registration requires admin approval."""
        resp = client.post("/api/auth/register", json={
            "name": "New Doctor",
            "email": "newdoc@test.com",
            "phone": "9999900003",
            "password": "Test@123",
            "role": "doctor",
        })
        assert resp.status_code == 400


# ═══════════════════════════════════════════════
# TOKEN & PROFILE TESTS
# ═══════════════════════════════════════════════

class TestProfileAndTokens:
    def test_get_profile_as_patient(self, client, patient_headers):
        """TC-AUTH-026: Authenticated patient can get their profile."""
        resp = client.get("/api/auth/me", headers=patient_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Ramesh Kumar"
        assert data["role"] == "patient"
        assert data["patient_id"] is not None

    def test_get_profile_as_doctor(self, client, doctor_headers):
        """TC-AUTH-027: Authenticated doctor can get their profile."""
        resp = client.get("/api/auth/me", headers=doctor_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Dr. Anjali Mehta"
        assert data["role"] == "doctor"
        assert data["specialization"] == "Cardiology"

    def test_get_profile_as_admin(self, client, admin_headers):
        """TC-AUTH-028: Authenticated admin can get their profile."""
        resp = client.get("/api/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "admin"

    def test_refresh_token(self, client):
        """TC-AUTH-029: Refresh token returns a new access token."""
        login_resp = client.post("/api/auth/login", json={"email": "ramesh@tms.com", "password": "Patient@123"})
        refresh_token = login_resp.json()["refresh_token"]
        resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_logout(self, client):
        """TC-AUTH-030: Logout blacklists the token."""
        login_resp = client.post("/api/auth/login", json={"email": "vikram@tms.com", "password": "Patient@123"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post("/api/auth/logout", headers=headers)
        assert resp.status_code == 200
        # Token should now be blocked
        resp2 = client.get("/api/auth/me", headers=headers)
        assert resp2.status_code == 401
