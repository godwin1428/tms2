"""
TMS — E2E Tests: Authentication & Authorization
Tests login, signup, role-based routing, and session management.
"""
import pytest
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ── Helpers ──
def navigate_to_login(driver, base_url):
    """Navigate to the login page."""
    driver.get(base_url)
    time.sleep(1)
    # Click 'Get Started' / Login link on home page
    try:
        # Try clicking the home page CTA that leads to login
        driver.execute_script("App.showLogin()")
        time.sleep(0.5)
    except:
        driver.get(base_url)
        time.sleep(0.5)
        driver.execute_script("App.showLogin()")
        time.sleep(0.5)


def do_login(driver, base_url, email, password):
    """Perform a full login flow."""
    navigate_to_login(driver, base_url)
    wait = WebDriverWait(driver, 5)
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-email")))
    email_input.clear()
    email_input.send_keys(email)
    pass_input = driver.find_element(By.ID, "login-password")
    pass_input.clear()
    pass_input.send_keys(password)
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(1.5)


def do_logout(driver):
    """Logout the current user."""
    try:
        driver.execute_script("App.logout()")
        time.sleep(0.5)
    except:
        pass


# ═══════════════════════════════════════════════
# LOGIN TESTS
# ═══════════════════════════════════════════════

class TestAdminLogin:
    def test_admin_login_success(self, driver, base_url):
        """TC-AUTH-001: Admin can login with valid credentials."""
        do_login(driver, base_url, "admin@tms.com", "Admin@123")
        # After successful admin login, the AdminPortal should render
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(kw in body_text.lower() for kw in ["admin", "dashboard", "analytics", "overview"]), \
            "Admin dashboard content not found after login"
        do_logout(driver)

    def test_admin_login_wrong_password(self, driver, base_url):
        """TC-AUTH-002: Admin login fails with wrong password."""
        do_login(driver, base_url, "admin@tms.com", "WrongPassword")
        # Should still be on login page
        login_page = driver.find_elements(By.ID, "login-email")
        assert len(login_page) > 0 or "login" in driver.page_source.lower(), \
            "Should remain on login page with wrong password"

    def test_admin_login_empty_password(self, driver, base_url):
        """TC-AUTH-003: Admin login fails with empty password."""
        do_login(driver, base_url, "admin@tms.com", "")
        login_page = driver.find_elements(By.ID, "login-email")
        assert len(login_page) > 0, "Should remain on login page with empty password"


class TestDoctorLogin:
    def test_doctor_login_success(self, driver, base_url):
        """TC-AUTH-004: Doctor can login with valid credentials."""
        do_login(driver, base_url, "anjali@tms.com", "Doctor@123")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(kw in body_text.lower() for kw in ["doctor", "schedule", "patients", "dashboard"]), \
            "Doctor dashboard not found after login"
        do_logout(driver)

    def test_doctor_login_wrong_password(self, driver, base_url):
        """TC-AUTH-005: Doctor login fails with wrong password."""
        do_login(driver, base_url, "anjali@tms.com", "wrong")
        login_page = driver.find_elements(By.ID, "login-email")
        assert len(login_page) > 0 or "login" in driver.page_source.lower()

    def test_doctor2_login_success(self, driver, base_url):
        """TC-AUTH-006: Second doctor can login."""
        do_login(driver, base_url, "rajesh@tms.com", "Doctor@123")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(kw in body_text.lower() for kw in ["doctor", "schedule", "dashboard"])
        do_logout(driver)


class TestPatientLogin:
    def test_patient_login_success(self, driver, base_url):
        """TC-AUTH-007: Patient can login with valid credentials."""
        do_login(driver, base_url, "ramesh@tms.com", "Patient@123")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(kw in body_text.lower() for kw in ["patient", "dashboard", "appointments", "doctors"]), \
            "Patient dashboard not found after login"
        do_logout(driver)

    def test_patient_login_wrong_password(self, driver, base_url):
        """TC-AUTH-008: Patient login fails with wrong password."""
        do_login(driver, base_url, "ramesh@tms.com", "bad")
        login_page = driver.find_elements(By.ID, "login-email")
        assert len(login_page) > 0 or "login" in driver.page_source.lower()

    def test_patient2_login_success(self, driver, base_url):
        """TC-AUTH-009: Second patient can login."""
        do_login(driver, base_url, "sunita@tms.com", "Patient@123")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(kw in body_text.lower() for kw in ["patient", "dashboard", "doctors"])
        do_logout(driver)


class TestInvalidLogin:
    def test_nonexistent_email(self, driver, base_url):
        """TC-AUTH-010: Login fails with non-existent email."""
        do_login(driver, base_url, "nobody@nowhere.com", "password123")
        login_page = driver.find_elements(By.ID, "login-email")
        assert len(login_page) > 0 or "login" in driver.page_source.lower()

    def test_empty_email(self, driver, base_url):
        """TC-AUTH-011: Login fails with empty email."""
        do_login(driver, base_url, "", "password")
        login_page = driver.find_elements(By.ID, "login-email")
        assert len(login_page) > 0

    def test_empty_both_fields(self, driver, base_url):
        """TC-AUTH-012: Login fails with both fields empty."""
        do_login(driver, base_url, "", "")
        login_page = driver.find_elements(By.ID, "login-email")
        assert len(login_page) > 0

    def test_sql_injection_attempt(self, driver, base_url):
        """TC-AUTH-013: Login is safe from SQL injection."""
        do_login(driver, base_url, "' OR 1=1 --", "' OR 1=1 --")
        login_page = driver.find_elements(By.ID, "login-email")
        assert len(login_page) > 0 or "login" in driver.page_source.lower()

    def test_xss_attempt_in_email(self, driver, base_url):
        """TC-AUTH-014: Login is safe from XSS in email field."""
        do_login(driver, base_url, "<script>alert('xss')</script>", "password")
        assert "<script>" not in driver.page_source


# ═══════════════════════════════════════════════
# SIGNUP TESTS
# ═══════════════════════════════════════════════

class TestSignup:
    def test_signup_form_renders(self, driver, base_url):
        """TC-AUTH-015: Signup form renders when tab is clicked."""
        navigate_to_login(driver, base_url)
        wait = WebDriverWait(driver, 5)
        tab = wait.until(EC.element_to_be_clickable((By.ID, "tab-signup")))
        tab.click()
        time.sleep(0.3)
        signup_form = driver.find_element(By.ID, "signup-form")
        assert signup_form.is_displayed(), "Signup form should be visible"

    def test_signup_patient_success(self, driver, base_url):
        """TC-AUTH-016: New patient can register successfully."""
        navigate_to_login(driver, base_url)
        wait = WebDriverWait(driver, 5)
        tab = wait.until(EC.element_to_be_clickable((By.ID, "tab-signup")))
        tab.click()
        time.sleep(0.3)

        uid = uuid.uuid4().hex[:6]
        driver.find_element(By.ID, "signup-name").send_keys(f"Test Patient {uid}")
        driver.find_element(By.ID, "signup-email").send_keys(f"testpat_{uid}@test.com")
        driver.find_element(By.ID, "signup-phone").send_keys("9999900001")
        driver.find_element(By.ID, "signup-password").send_keys("Test@123")
        driver.find_element(By.ID, "signup-btn").click()
        time.sleep(1.5)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(kw in body_text.lower() for kw in ["patient", "dashboard", "doctors"]), \
            "Should redirect to patient dashboard after signup"
        do_logout(driver)

    def test_signup_missing_name(self, driver, base_url):
        """TC-AUTH-017: Signup fails without name."""
        navigate_to_login(driver, base_url)
        wait = WebDriverWait(driver, 5)
        tab = wait.until(EC.element_to_be_clickable((By.ID, "tab-signup")))
        tab.click()
        time.sleep(0.3)

        driver.find_element(By.ID, "signup-email").send_keys("noname@test.com")
        driver.find_element(By.ID, "signup-password").send_keys("Test@123")
        driver.find_element(By.ID, "signup-btn").click()
        time.sleep(0.5)

        # Should still be on the signup form
        signup_form = driver.find_element(By.ID, "signup-form")
        assert signup_form.is_displayed()

    def test_signup_short_password(self, driver, base_url):
        """TC-AUTH-018: Signup fails with password < 6 chars."""
        navigate_to_login(driver, base_url)
        wait = WebDriverWait(driver, 5)
        tab = wait.until(EC.element_to_be_clickable((By.ID, "tab-signup")))
        tab.click()
        time.sleep(0.3)

        driver.find_element(By.ID, "signup-name").send_keys("Short Pass")
        driver.find_element(By.ID, "signup-email").send_keys("short@test.com")
        driver.find_element(By.ID, "signup-password").send_keys("abc")
        driver.find_element(By.ID, "signup-btn").click()
        time.sleep(0.5)

        signup_form = driver.find_element(By.ID, "signup-form")
        assert signup_form.is_displayed()

    def test_signup_tab_switch(self, driver, base_url):
        """TC-AUTH-019: Can switch between login and signup tabs."""
        navigate_to_login(driver, base_url)
        wait = WebDriverWait(driver, 5)
        tab_signup = wait.until(EC.element_to_be_clickable((By.ID, "tab-signup")))
        tab_signup.click()
        time.sleep(0.3)
        assert driver.find_element(By.ID, "signup-form").is_displayed()

        driver.find_element(By.ID, "tab-login").click()
        time.sleep(0.3)
        assert driver.find_element(By.ID, "login-form").is_displayed()

    def test_login_page_has_demo_credentials(self, driver, base_url):
        """TC-AUTH-020: Login page shows demo account credentials."""
        navigate_to_login(driver, base_url)
        time.sleep(0.3)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "admin@tms.com" in page_text, "Demo credentials should be visible"
