#!/usr/bin/env python3
"""
Test script for employee creation API
"""
import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = 'http://127.0.0.1:8000'
EMPLOYEES_URL = f'{BASE_URL}/api/employees/'

# Test employee data
test_employee = {
    "employee_id": "EMP-TEST-001",
    "first_name": "Test",
    "last_name": "Employee",
    "middle_name": "API",
    "email": "test.employee@sdca.edu.ph",
    "mobile_no": "+639123456789",
    "present_address": "123 Test Street, Test City",
    "birth_date": "1990-01-15",  # YYYY-MM-DD format
    "birth_place": "Test City",
    "age": 34,
    "gender": "Male",
    "civil_status": "Single",
    "date_hired": "2024-01-15",  # YYYY-MM-DD format
    "position": 1,  # Assuming position ID 1 exists
    "department": 1,  # Assuming department ID 1 exists
    "office": 1,  # Assuming office ID 1 exists
    "password": "test123456"  # Optional, will default to sdca2025
}

def test_employee_creation():
    """Test creating an employee via API"""
    print("Testing employee creation...")
    print(f"POST {EMPLOYEES_URL}")
    print(f"Data: {json.dumps(test_employee, indent=2)}")
    
    try:
        response = requests.post(EMPLOYEES_URL, json=test_employee)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ Employee created successfully!")
            employee_data = response.json()
            print(f"Created employee: {employee_data.get('full_name')} (ID: {employee_data.get('id')})")
        else:
            print("❌ Employee creation failed!")
            try:
                error_data = response.json()
                print(f"Errors: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response text: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_different_date_formats():
    """Test with different date formats"""
    test_cases = [
        {"birth_date": "1990-01-15", "date_hired": "2024-01-15", "format": "YYYY-MM-DD"},
        {"birth_date": "01/15/1990", "date_hired": "01/15/2024", "format": "MM/DD/YYYY"},
        {"birth_date": "15/01/1990", "date_hired": "15/01/2024", "format": "DD/MM/YYYY"},
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['format']} ---")
        
        test_data = test_employee.copy()
        test_data["employee_id"] = f"EMP-TEST-{i+1:03d}"
        test_data["email"] = f"test{i+1}@sdca.edu.ph"
        test_data["birth_date"] = test_case["birth_date"]
        test_data["date_hired"] = test_case["date_hired"]
        
        try:
            response = requests.post(EMPLOYEES_URL, json=test_data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                print(f"✅ Success with {test_case['format']} format")
            else:
                print(f"❌ Failed with {test_case['format']} format")
                try:
                    error_data = response.json()
                    print(f"Errors: {error_data}")
                except:
                    print(f"Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Employee Creation API Test")
    print("=" * 50)
    
    # Test basic creation
    test_employee_creation()
    
    print("\n" + "=" * 50)
    print("Testing different date formats...")
    test_with_different_date_formats()
