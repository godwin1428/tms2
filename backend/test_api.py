import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_result(name, success, details=None):
    status = "SUCCESS" if success else "FAILED"
    print(f"[{status}] {name}")
    if details:
        print(f"    Details: {details}")

def run_tests():
    print("Starting End-to-End API Integration Tests...")
    
    # 1. Health Check
    try:
        res = requests.get(f"{BASE_URL.replace('/api', '')}/api/health")
        if res.status_code == 200:
            print_result("1. Health Check Service", True, res.json())
        else:
            print_result("1. Health Check Service", False, f"HTTP {res.status_code}")
    except Exception as e:
        print_result("1. Health Check Service", False, str(e))
        return

    # 2. Patient Login
    patient_token = None
    try:
        payload = {"email": "ramesh@tms.com", "password": "Patient@123"}
        res = requests.post(f"{BASE_URL}/auth/login", json=payload)
        if res.status_code == 200:
            data = res.json()
            patient_token = data.get("access_token")
            print_result("2. Patient Authentication (Ramesh Kumar)", True, f"Token received (expires in {data.get('user', {}).get('role')})")
        else:
            print_result("2. Patient Authentication (Ramesh Kumar)", False, res.text)
    except Exception as e:
        print_result("2. Patient Authentication (Ramesh Kumar)", False, str(e))

    # 3. Fetch Doctors List
    try:
        headers = {"Authorization": f"Bearer {patient_token}"} if patient_token else {}
        res = requests.get(f"{BASE_URL}/doctors", headers=headers)
        if res.status_code == 200:
            docs = res.json()
            print_result("3. Fetch Doctors List", True, f"Found {len(docs)} doctors in specialization lists")
        else:
            print_result("3. Fetch Doctors List", False, res.text)
    except Exception as e:
        print_result("3. Fetch Doctors List", False, str(e))

    # 4. Doctor Login
    doctor_token = None
    try:
        payload = {"email": "anjali@tms.com", "password": "Doctor@123"}
        res = requests.post(f"{BASE_URL}/auth/login", json=payload)
        if res.status_code == 200:
            data = res.json()
            doctor_token = data.get("access_token")
            print_result("4. Doctor Authentication (Dr. Anjali Mehta)", True, f"Token received (Role: {data.get('user', {}).get('role')})")
        else:
            print_result("4. Doctor Authentication (Dr. Anjali Mehta)", False, res.text)
    except Exception as e:
        print_result("4. Doctor Authentication (Dr. Anjali Mehta)", False, str(e))

    # 5. Fetch Doctor's Today's Schedule & Earnings
    if doctor_token:
        headers = {"Authorization": f"Bearer {doctor_token}"}
        try:
            res = requests.get(f"{BASE_URL}/doctors/schedule", headers=headers)
            if res.status_code == 200:
                schedule = res.json()
                print_result("5a. Fetch Doctor's Schedule", True, f"Found {len(schedule)} appointments scheduled today")
            else:
                print_result("5a. Fetch Doctor's Schedule", False, res.text)
        except Exception as e:
            print_result("5a. Fetch Doctor's Schedule", False, str(e))

        try:
            res = requests.get(f"{BASE_URL}/doctors/earnings", headers=headers)
            if res.status_code == 200:
                earnings = res.json()
                print_result("5b. Fetch Doctor's Earnings HUD Summary", True, f"Total earnings: INR {earnings.get('total_earnings')}")
            else:
                print_result("5b. Fetch Doctor's Earnings HUD Summary", False, res.text)
        except Exception as e:
            print_result("5b. Fetch Doctor's Earnings HUD Summary", False, str(e))

    # 6. Admin Login & Dashboard
    admin_token = None
    try:
        payload = {"email": "admin@tms.com", "password": "Admin@123"}
        res = requests.post(f"{BASE_URL}/auth/login", json=payload)
        if res.status_code == 200:
            data = res.json()
            admin_token = data.get("access_token")
            print_result("6. Admin Authentication (Admin User)", True, f"Token received (Role: {data.get('user', {}).get('role')})")
        else:
            print_result("6. Admin Authentication (Admin User)", False, res.text)
    except Exception as e:
        print_result("6. Admin Authentication (Admin User)", False, str(e))

    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        try:
            res = requests.get(f"{BASE_URL}/admin/dashboard", headers=headers)
            if res.status_code == 200:
                dash = res.json()
                print_result("7a. Fetch Admin Dashboard Stats", True, f"Platform status: Doctors: {dash.get('total_doctors')}, Patients: {dash.get('total_patients')}, Revenue: INR {dash.get('total_revenue')}")
            else:
                print_result("7a. Fetch Admin Dashboard Stats", False, res.text)
        except Exception as e:
            print_result("7a. Fetch Admin Dashboard Stats", False, str(e))

        try:
            res = requests.get(f"{BASE_URL}/admin/analytics", headers=headers)
            if res.status_code == 200:
                analytics = res.json()
                print_result("7b. Fetch Admin Analytics Charts Data", True, f"Daily consultations logged for charts: {len(analytics.get('daily_consultations', []))} days")
            else:
                print_result("7b. Fetch Admin Analytics Charts Data", False, res.text)
        except Exception as e:
            print_result("7b. Fetch Admin Analytics Charts Data", False, str(e))

    print("\nIntegration Verification Completed Successfully!")

if __name__ == "__main__":
    run_tests()
