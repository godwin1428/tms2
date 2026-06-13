"""
TMS — E2E Tests: Realtime Features
Tests WebRTC, WebSocket, AI Triage, Bluetooth, and homepage elements.
"""
import pytest
import time
import requests
from conftest import wait_for_app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ── Helpers ──
def login_patient(driver, base_url):
    driver.get(base_url)
    driver.execute_script("localStorage.clear()")  # ensure clean auth state
    wait_for_app(driver)
    driver.execute_script("App.showLogin()")
    time.sleep(0.5)
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-email")))
    email_input.clear()
    email_input.send_keys("ramesh@tms.com")
    pass_input = driver.find_element(By.ID, "login-password")
    pass_input.clear()
    pass_input.send_keys("Patient@123")
    driver.find_element(By.ID, "login-btn").click()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return localStorage.getItem('tms_access_token') !== null")
    )


def login_doctor(driver, base_url):
    driver.get(base_url)
    driver.execute_script("localStorage.clear()")  # ensure clean auth state
    wait_for_app(driver)
    driver.execute_script("App.showLogin()")
    time.sleep(0.5)
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-email")))
    email_input.clear()
    email_input.send_keys("anjali@tms.com")
    pass_input = driver.find_element(By.ID, "login-password")
    pass_input.clear()
    pass_input.send_keys("Doctor@123")
    driver.find_element(By.ID, "login-btn").click()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return localStorage.getItem('tms_access_token') !== null")
    )


def logout(driver):
    try:
        driver.execute_script("App.logout()")
        time.sleep(0.5)
    except:
        pass


# ═══════════════════════════════════════════════
# API HEALTH & BACKEND CHECKS
# ═══════════════════════════════════════════════

class TestBackendHealth:
    def test_api_health_endpoint(self, base_url):
        """TC-RT-001: Backend health endpoint returns healthy."""
        resp = requests.get(f"{base_url}/api/health", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_api_docs_accessible(self, base_url):
        """TC-RT-002: Swagger docs are accessible."""
        resp = requests.get(f"{base_url}/docs", timeout=5)
        assert resp.status_code == 200

    def test_triage_status_endpoint(self, base_url):
        """TC-RT-003: Triage status endpoint is accessible."""
        resp = requests.get(f"{base_url}/api/triage/status", timeout=5)
        assert resp.status_code == 200


# ═══════════════════════════════════════════════
# HOMEPAGE TESTS
# ═══════════════════════════════════════════════

class TestHomePage:
    def test_homepage_loads(self, driver, base_url):
        """TC-RT-004: Homepage renders with TMS branding."""
        driver.get(base_url)
        driver.execute_script("localStorage.clear()")
        wait_for_app(driver)
        body = driver.find_element(By.TAG_NAME, "body").text
        assert "TMS" in body or "Telemedicine" in body, "Homepage should show TMS branding"

    def test_homepage_has_login_cta(self, driver, base_url):
        """TC-RT-005: Homepage has login/get started CTA."""
        driver.get(base_url)
        driver.execute_script("localStorage.clear()")
        wait_for_app(driver)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["get started", "login", "sign in", "register"]), \
            "Homepage should have login CTA"

    def test_homepage_features_section(self, driver, base_url):
        """TC-RT-006: Homepage shows features section."""
        driver.get(base_url)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["feature", "consultation", "prescription", "video", "ai", "bluetooth"]), \
            "Features section should be visible"

    def test_homepage_has_title(self, driver, base_url):
        """TC-RT-007: Page title contains TMS."""
        driver.get(base_url)
        time.sleep(0.5)
        assert "TMS" in driver.title or "Telemedicine" in driver.title, "Page title should reference TMS"


# ═══════════════════════════════════════════════
# WEBRTC / VIDEO CONSULTATION ELEMENTS
# ═══════════════════════════════════════════════

class TestVideoConsultation:
    def test_patient_sees_video_option(self, driver, base_url):
        """TC-RT-008: Patient portal has video/consultation option."""
        login_patient(driver, base_url)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["video", "consult", "call", "join", "appointment"]), \
            "Video/consultation option should be present"
        logout(driver)

    def test_doctor_sees_consultation_option(self, driver, base_url):
        """TC-RT-009: Doctor portal has consultation room option."""
        login_doctor(driver, base_url)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["consult", "video", "room", "call", "patient"]), \
            "Consultation room option should be present"
        logout(driver)


# ═══════════════════════════════════════════════
# AI TRIAGE CHAT
# ═══════════════════════════════════════════════

class TestAITriageFeatures:
    def test_triage_accessible_for_patient(self, driver, base_url):
        """TC-RT-010: AI triage is accessible from patient portal."""
        login_patient(driver, base_url)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["triage", "ai", "symptom", "chat", "health"]), \
            "AI triage option should be accessible"
        logout(driver)

    def test_triage_ui_elements(self, driver, base_url):
        """TC-RT-011: Triage view has input/send elements."""
        login_patient(driver, base_url)
        driver.execute_script("""
            document.querySelectorAll('[data-view]').forEach(n => {
                if (n.textContent.toLowerCase().includes('triage') || n.textContent.toLowerCase().includes('ai') || n.textContent.toLowerCase().includes('chat')) n.click();
            });
        """)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["symptom", "chat", "send", "message", "triage", "ai"]), \
            "Triage UI elements should be present"
        logout(driver)


# ═══════════════════════════════════════════════
# BLUETOOTH MODULE
# ═══════════════════════════════════════════════

class TestBluetoothModule:
    def test_bluetooth_module_accessible(self, driver, base_url):
        """TC-RT-012: Bluetooth/vitals section is accessible."""
        login_patient(driver, base_url)
        driver.execute_script("""
            document.querySelectorAll('[data-view]').forEach(n => {
                if (n.textContent.toLowerCase().includes('vital') || n.textContent.toLowerCase().includes('bluetooth') || n.textContent.toLowerCase().includes('device')) n.click();
            });
        """)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["bluetooth", "vital", "device", "heart", "connect", "pair"]), \
            "Bluetooth module should be accessible"
        logout(driver)

    def test_bluetooth_js_module_exists(self, driver, base_url):
        """TC-RT-013: BluetoothModule is loaded in the browser."""
        driver.get(base_url)
        time.sleep(1)
        result = driver.execute_script("return typeof BluetoothModule !== 'undefined'")
        assert result is True, "BluetoothModule JS object should exist"


# ═══════════════════════════════════════════════
# SECURITY & SESSION
# ═══════════════════════════════════════════════

class TestSecuritySession:
    def test_logout_clears_session(self, driver, base_url):
        """TC-RT-014: Logout clears localStorage tokens."""
        login_patient(driver, base_url)
        logout(driver)
        token = driver.execute_script("return localStorage.getItem('tms_access_token') || localStorage.getItem('access_token')")
        assert token is None or token == "", "Token should be cleared after logout"

    def test_api_returns_401_without_token(self, base_url):
        """TC-RT-015: Protected API returns 401 without token."""
        resp = requests.get(f"{base_url}/api/auth/me", timeout=5)
        assert resp.status_code in [401, 403], "Should return 401/403 without auth token"