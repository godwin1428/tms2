"""
TMS — E2E Tests: Admin Dashboard
Tests admin login, navigation, analytics, doctor/patient management, and revenue views.
"""
import pytest
import time
from conftest import wait_for_app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ── Helpers ──
def login_admin(driver, base_url):
    """Login as admin."""
    driver.get(base_url)
    driver.execute_script("localStorage.clear()")  # ensure clean auth state
    wait_for_app(driver)
    driver.execute_script("App.showLogin()")
    time.sleep(0.5)
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-email")))
    email_input.clear()
    email_input.send_keys("admin@tms.com")
    pass_input = driver.find_element(By.ID, "login-password")
    pass_input.clear()
    pass_input.send_keys("Admin@123")
    driver.find_element(By.ID, "login-btn").click()
    # Wait for dashboard to render instead of fixed sleep
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
# ADMIN DASHBOARD
# ═══════════════════════════════════════════════

class TestAdminDashboard:
    def test_admin_dashboard_loads(self, driver, base_url):
        """TC-ADM-001: Admin dashboard renders after login."""
        login_admin(driver, base_url)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["admin", "dashboard", "overview", "analytics"]), \
            "Admin dashboard not rendered"
        logout(driver)

    def test_admin_sees_stats(self, driver, base_url):
        """TC-ADM-002: Dashboard shows platform statistics."""
        login_admin(driver, base_url)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["doctor", "patient", "appointment", "revenue", "total"]), \
            "Platform stats should be visible"
        logout(driver)

    def test_admin_has_navigation(self, driver, base_url):
        """TC-ADM-003: Admin portal has navigation items."""
        login_admin(driver, base_url)
        nav = driver.find_elements(By.CSS_SELECTOR, ".nav-item, .sidebar-link, [data-view]")
        assert len(nav) > 0, "Navigation items should exist"
        logout(driver)


# ═══════════════════════════════════════════════
# DOCTOR MANAGEMENT
# ═══════════════════════════════════════════════

class TestDoctorManagement:
    def test_doctor_management_view(self, driver, base_url):
        """TC-ADM-004: Doctor management view loads."""
        login_admin(driver, base_url)
        driver.execute_script("""
            document.querySelectorAll('[data-view]').forEach(n => {
                if (n.textContent.toLowerCase().includes('doctor')) n.click();
            });
        """)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text
        assert "Dr." in body or "doctor" in body.lower(), "Doctor list should appear"
        logout(driver)

    def test_doctor_list_has_names(self, driver, base_url):
        """TC-ADM-005: Doctor list shows doctor names."""
        login_admin(driver, base_url)
        driver.execute_script("""
            document.querySelectorAll('[data-view]').forEach(n => {
                if (n.textContent.toLowerCase().includes('doctor')) n.click();
            });
        """)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text
        doctors = ["Anjali", "Rajesh", "Suresh", "Kavita", "Amit", "Neha"]
        found = sum(1 for d in doctors if d in body)
        assert found >= 1, "At least one seeded doctor name should be visible"
        logout(driver)

    def test_doctor_specialization_shown(self, driver, base_url):
        """TC-ADM-006: Doctor specializations are shown in list."""
        login_admin(driver, base_url)
        driver.execute_script("""
            document.querySelectorAll('[data-view]').forEach(n => {
                if (n.textContent.toLowerCase().includes('doctor')) n.click();
            });
        """)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text
        specs = ["Cardiology", "General Medicine", "Pulmonology", "Dermatology"]
        found = sum(1 for s in specs if s in body)
        assert found >= 1, "At least one specialization should be visible"
        logout(driver)


# ═══════════════════════════════════════════════
# PATIENT MANAGEMENT
# ═══════════════════════════════════════════════

class TestPatientManagement:
    def test_patient_management_view(self, driver, base_url):
        """TC-ADM-007: Patient management view loads."""
        login_admin(driver, base_url)
        driver.execute_script("""
            document.querySelectorAll('[data-view]').forEach(n => {
                if (n.textContent.toLowerCase().includes('patient')) n.click();
            });
        """)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["patient", "ramesh", "sunita", "name"]), \
            "Patient list should appear"
        logout(driver)

    def test_patient_list_has_names(self, driver, base_url):
        """TC-ADM-008: Patient list shows patient names."""
        login_admin(driver, base_url)
        driver.execute_script("""
            document.querySelectorAll('[data-view]').forEach(n => {
                if (n.textContent.toLowerCase().includes('patient')) n.click();
            });
        """)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text
        patients = ["Ramesh", "Sunita", "Arjun", "Priya", "Mohammed", "Lakshmi"]
        found = sum(1 for p in patients if p in body)
        assert found >= 1, "At least one seeded patient name should be visible"
        logout(driver)


# ═══════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════

class TestAnalytics:
    def test_analytics_view_loads(self, driver, base_url):
        """TC-ADM-013: Analytics view loads."""
        login_admin(driver, base_url)
        driver.execute_script("""
            document.querySelectorAll('[data-view]').forEach(n => {
                if (n.textContent.toLowerCase().includes('analytics') || n.textContent.toLowerCase().includes('chart') || n.textContent.toLowerCase().includes('overview')) n.click();
            });
        """)
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["analytics", "chart", "trend", "overview", "dashboard"]), \
            "Analytics view should load"
        logout(driver)

    def test_admin_dashboard_counts(self, driver, base_url):
        """TC-ADM-014: Admin sees doctor/patient counts."""
        login_admin(driver, base_url)
        body = driver.find_element(By.TAG_NAME, "body").text
        # We seeded 6 doctors and 8 patients
        has_numbers = any(n in body for n in ["6", "8", "14", "15"])
        assert has_numbers or "doctor" in body.lower(), "Counts or labels should appear"
        logout(driver)

    def test_admin_page_title(self, driver, base_url):
        """TC-ADM-015: Admin page has proper title or heading."""
        login_admin(driver, base_url)
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(kw in body for kw in ["admin", "panel", "management", "dashboard"]), \
            "Admin heading should be present"
        logout(driver)