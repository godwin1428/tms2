"""
TMS — E2E Selenium Test Configuration
Fixtures for WebDriver, backend server, and Excel report generation.
"""
import os
import sys
import time
import socket
import subprocess
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import pandas as pd
from datetime import datetime

# ── Globals for test result collection ──
test_results = []
suite_start_time = None

from webdriver_manager.chrome import ChromeDriverManager
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
BASE_URL = "http://127.0.0.1:8000"


# ── Helpers ──
def is_port_open(port, host="127.0.0.1", timeout=1):
    """Check if a TCP port is open."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False


# ── Pytest hooks ──
def pytest_configure(config):
    global suite_start_time
    suite_start_time = datetime.now()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        # Derive category from the module filename
        module_name = os.path.basename(item.module.__file__).replace("test_", "").replace(".py", "")
        category_map = {
            "auth": "Authentication",
            "patient_dashboard": "Patient Dashboard",
            "doctor_dashboard": "Doctor Dashboard",
            "admin_dashboard": "Admin Dashboard",
            "realtime_features": "Realtime Features",
        }
        category = category_map.get(module_name, module_name.replace("_", " ").title())

        test_results.append({
            "No.": len(test_results) + 1,
            "Category": category,
            "Test Name": item.name,
            "Status": "Passed" if report.passed else "Failed",
            "Error Details": str(report.longrepr)[:500] if report.failed else "",
        })


def pytest_sessionfinish(session, exitstatus):
    end_time = datetime.now()
    duration = (end_time - suite_start_time).total_seconds()

    passed_count = sum(1 for t in test_results if t["Status"] == "Passed")
    failed_count = sum(1 for t in test_results if t["Status"] == "Failed")
    total_count = len(test_results)
    pass_rate = round((passed_count / total_count * 100), 2) if total_count > 0 else 0

    overall_status = "✅ ALL PASSED" if failed_count == 0 else f"❌ {failed_count} FAILED"

    summary_data = [{
        "Test Suite": "TMS E2E Functionality Tests",
        "Overall Status": overall_status,
        "Total Tests": total_count,
        "Passed": passed_count,
        "Failed": failed_count,
        "Pass Rate %": pass_rate,
        "Duration (sec)": round(duration, 2),
        "Start Time": suite_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
    }]

    details_df = pd.DataFrame(test_results)
    if details_df.empty:
        details_df = pd.DataFrame(columns=["No.", "Category", "Test Name", "Status", "Error Details"])

    passed_df = details_df[details_df["Status"] == "Passed"].copy() if not details_df.empty else pd.DataFrame()
    failed_df = details_df[details_df["Status"] == "Failed"].copy() if not details_df.empty else pd.DataFrame()

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"E2E_Test_Report_TMS_{timestamp}.xlsx")

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
        passed_df.to_excel(writer, sheet_name="Passed Tests", index=False)
        failed_df.to_excel(writer, sheet_name="Failed Tests", index=False)
        details_df.to_excel(writer, sheet_name="Execution Log", index=False)
        details_df.to_excel(writer, sheet_name="Test Details", index=False)

    print(f"\n{'='*60}")
    print(f"  EXCEL TEST REPORT: {report_path}")
    print(f"  Total: {total_count}  |  Passed: {passed_count}  |  Failed: {failed_count}  |  Rate: {pass_rate}%")
    print(f"{'='*60}")


# ── Fixtures ──

@pytest.fixture(scope="session")
def backend_server():
    """Start the FastAPI backend server if not already running."""
    if is_port_open(8000):
        print("[Fixture] Backend already running on port 8000.")
        yield
        return

    print("[Fixture] Starting backend server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )

    # Wait for server to be ready
    for _ in range(60):
        if is_port_open(8000):
            print("[Fixture] Backend server ready.")
            break
        time.sleep(1)
    else:
        stdout, stderr = proc.communicate(timeout=5)
        proc.kill()
        raise RuntimeError(
            f"Backend server did not start within 60 seconds.\n"
            f"STDOUT: {stdout.decode()[-2000:]}\n"
            f"STDERR: {stderr.decode()[-2000:]}"
        )

    yield

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="session")
def base_url(backend_server):
    return BASE_URL


def _ensure_executable(path: str):
    """Ensure the given file is executable."""
    if os.path.isfile(path) and not os.access(path, os.X_OK):
        os.chmod(path, 0o755)

def _resolve_chromedriver() -> str:
    import shutil
    # 1. $CHROMEDRIVER_PATH — set by browser-actions/setup-chrome on CI
    env_path = os.environ.get("CHROMEDRIVER_PATH")
    if env_path and os.path.isfile(env_path):
        _ensure_executable(env_path)
        return env_path

    # 2. chromedriver already on PATH (some CI runners have it)
    which_path = shutil.which("chromedriver")
    if which_path:
        _ensure_executable(which_path)
        return which_path

    # 3. webdriver-manager download — local dev fallback only
    from webdriver_manager.chrome import ChromeDriverManager
    driver_path = ChromeDriverManager().install()
    
    if "THIRD_PARTY_NOTICES" in driver_path or "LICENSE" in driver_path:
        import sys
        driver_dir = os.path.dirname(driver_path)
        driver_name = "chromedriver.exe" if sys.platform == "win32" else "chromedriver"
        driver_path = os.path.join(driver_dir, driver_name)
    
    _ensure_executable(driver_path)
    return driver_path

@pytest.fixture(scope="session")
def driver():
    """Create a headless Chrome WebDriver for the full session."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-insecure-localhost")

    driver_path = _resolve_chromedriver()
    service = ChromeService(executable_path=driver_path)
    d = webdriver.Chrome(service=service, options=options)
    d.implicitly_wait(3)

    yield d

    d.quit()


# ── Shared JS-readiness helper ──
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException

def wait_for_app(driver, timeout=20):
    """Wait until the App JS object is defined on the page."""
    import time as _time
    deadline = _time.monotonic() + timeout
    while _time.monotonic() < deadline:
        try:
            ready = driver.execute_script(
                "return document.readyState === 'complete' && "
                "typeof App !== 'undefined' && "
                "typeof App.showLogin === 'function'"
            )
            if ready:
                return
        except WebDriverException:
            pass  # page still navigating — keep polling
        _time.sleep(0.3)
    raise TimeoutException("App JS object not ready within timeout")