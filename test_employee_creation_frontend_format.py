#!/usr/bin/env python3
"""
Test script to verify frontend date formatting is working properly
"""

import requests
import json
from datetime import datetime

# Test employee data with dates formatted as they would come from frontend
test_employee = {
    "employee_id": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "first_name": "Test",
    "last_name": "Employee",
    "email": f"test.employee.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "mobile_no": "09123456789",
    "present_address": "123 Test Street",
    "birth_date": "1990-05-15",  # YYYY-MM-DD format from frontend
    "birth_place": "Test City",
    "age": 33,
    "gender": "Male",
    "citizenship": "Filipino",
    "civil_status": "Single",
    "date_hired": "2023-01-15",  # YYYY-MM-DD format from frontend
    "position": 1,
    "department": 1,
    "office": 1,
    "password": "sdca2025"
}

def test_employee_creation():
    url = "http://127.0.0.1:8000/api/employees/"
    
    try:
        print("Testing employee creation with frontend-formatted dates...")
        print(f"Birth Date: {test_employee['birth_date']}")
        print(f"Date Hired: {test_employee['date_hired']}")
        
        response = requests.post(url, json=test_employee)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 201:
            employee_data = response.json()
            print("✅ Employee created successfully!")
            print(f"Employee ID: {employee_data.get('employee_id')}")
            print(f"Birth Date in response: {employee_data.get('birth_date')}")
            print(f"Date Hired in response: {employee_data.get('date_hired')}")
        else:
            print("❌ Employee creation failed!")
            try:
                error_data = response.json()
                print("Error details:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Error: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_employee_creation()
