import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random
import string

BASE_URL = "https://tms2-1.onrender.com/"

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def generate_random_email():
    chars = string.ascii_lowercase + string.digits
    return f"test_{''.join(random.choice(chars) for _ in range(8))}@example.com"

def test_signup_and_login_flow(driver):
    print("Navigating to home page...")
    driver.get(BASE_URL)
    
    # Wait for the page to load and display the home nav
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "home-nav"))
    )
    time.sleep(2) # Natural delay
    
    print("Clicking login button on navigation...")
    login_btn = driver.find_element(By.ID, "nav-login-btn")
    driver.execute_script("arguments[0].click();", login_btn)
    time.sleep(2) # Natural delay
    
    print("Switching to signup tab...")
    signup_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "tab-signup"))
    )
    driver.execute_script("arguments[0].click();", signup_tab)
    time.sleep(1) # Natural delay
    
    # Fill out signup form
    print("Filling out signup form...")
    random_email = generate_random_email()
    random_pass = "TestPass123!"
    
    driver.find_element(By.ID, "signup-name").send_keys("Automated Test User")
    time.sleep(0.5)
    driver.find_element(By.ID, "signup-email").send_keys(random_email)
    time.sleep(0.5)
    driver.find_element(By.ID, "signup-phone").send_keys("9876543210")
    time.sleep(0.5)
    driver.find_element(By.ID, "signup-password").send_keys(random_pass)
    time.sleep(1)
    
    # Assuming Patient is default selected role, we can fill patient fields
    driver.find_element(By.ID, "signup-age").send_keys("30")
    time.sleep(1)
    
    print("Submitting signup form...")
    signup_submit_btn = driver.find_element(By.ID, "signup-btn")
    driver.execute_script("arguments[0].click();", signup_submit_btn)
    
    # After signup, user should be redirected to patient portal or show success toast
    print("Waiting for redirection or success...")
    time.sleep(5) # Wait for API response and redirection
    
    # Verify patient portal loaded
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "portal-sidebar"))
        )
        print("Successfully reached portal!")
    except Exception as e:
        print("Could not find portal sidebar, checking if we are logged in...")
        
    print("Logging out...")
    # Find logout button. Typically in sidebar or profile menu.
    try:
        logout_btn = driver.find_element(By.ID, "btn-logout")
        driver.execute_script("arguments[0].click();", logout_btn)
        time.sleep(3)
    except:
        print("Could not find logout button directly, proceeding to manual login test...")
    
    # Now let's test login explicitly
    print("Navigating to home page for login test...")
    driver.get(BASE_URL)
    time.sleep(2)
    
    print("Clicking login button...")
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "nav-login-btn"))
    )
    driver.execute_script("arguments[0].click();", login_btn)
    time.sleep(2)
    
    print("Filling out login form...")
    driver.find_element(By.ID, "login-email").send_keys(random_email)
    time.sleep(0.5)
    driver.find_element(By.ID, "login-password").send_keys(random_pass)
    time.sleep(1)
    
    print("Submitting login form...")
    login_submit_btn = driver.find_element(By.ID, "login-btn")
    driver.execute_script("arguments[0].click();", login_submit_btn)
    
    print("Waiting for portal access...")
    time.sleep(5)
    
    # Verify login success
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "portal-layout"))
    )
    print("Login test successful!")
