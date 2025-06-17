import requests
import json

# API base URL
BASE_URL = 'http://localhost:8000'

def test_authentication():
    """Test employee authentication"""
    print("=== Testing Authentication ===")
    
    # Test with a regular employee (Faculty)
    login_data = {
        "email": "jennifer.davis@university.edu",  # Program Chair
        "password": "sdca2025"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"Login Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Login Success: {data['employee']['full_name']}")
        print(f"Position: {data['employee']['position_title']}")
        print(f"Token: {data['token'][:20]}...")
        return data['token'], data['employee']
    else:
        print(f"Login Failed: {response.text}")
        return None, None

def test_role_based_endpoints(token, employee):
    """Test role-based leave management endpoints"""
    print(f"\n=== Testing Role-Based Endpoints for {employee['full_name']} ===")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Test approval hierarchy
    print("\n--- Testing Approval Hierarchy ---")
    response = requests.get(f"{BASE_URL}/api/leave-requests/approval_hierarchy/", headers=headers)
    print(f"Approval Hierarchy Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Employee Role Level: {data['employee']['role_level']}")
        print(f"Potential Approvers: {len(data['potential_approvers'])}")
        for approver in data['potential_approvers']:
            print(f"  - {approver['name']} ({approver['position']}, Level {approver['role_level']})")
    
    # Test pending approvals
    print("\n--- Testing Pending Approvals ---")
    response = requests.get(f"{BASE_URL}/api/leave-requests/pending_for_approval/", headers=headers)
    print(f"Pending Approvals Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Approver: {data['approver_info']['name']}")
        print(f"Role Level: {data['approver_info']['role_level']}")
        print(f"Approval Scope: {data['approver_info']['approval_scope']}")
        print(f"Pending Requests: {len(data['requests'])}")
    else:
        print(f"Error: {response.text}")

def test_different_roles():
    """Test different employee roles"""
    # Test employees with different roles
    test_employees = [
        ("robert.williams@university.edu", "VPAA - Should approve all"),
        ("michael.brown@university.edu", "Dean - Should approve department"),
        ("jennifer.davis@university.edu", "PC - Should approve program"),
        ("david.wilson@university.edu", "Faculty - Should not approve")
    ]
    
    for email, description in test_employees:
        print(f"\n{'='*50}")
        print(f"Testing: {description}")
        print(f"Email: {email}")
        
        login_data = {"email": email, "password": "sdca2025"}
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data['token']
            employee = data['employee']
            
            print(f"✓ Login successful: {employee['full_name']}")
            print(f"  Position: {employee['position_title']}")
            
            # Test role-based endpoints
            headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
            
            # Test approval hierarchy
            response = requests.get(f"{BASE_URL}/api/leave-requests/approval_hierarchy/", headers=headers)
            if response.status_code == 200:
                hierarchy_data = response.json()
                print(f"  Role Level: {hierarchy_data['employee']['role_level']}")
                print(f"  Potential Approvers: {len(hierarchy_data['potential_approvers'])}")
            
            # Test pending approvals
            response = requests.get(f"{BASE_URL}/api/leave-requests/pending_for_approval/", headers=headers)
            if response.status_code == 200:
                approval_data = response.json()
                print(f"  Can approve: ✓ (Scope: {approval_data['approver_info']['approval_scope']})")
                print(f"  Pending requests: {len(approval_data['requests'])}")
            elif response.status_code == 403:
                print(f"  Can approve: ✗ (No permission)")
            else:
                print(f"  Error: {response.status_code}")
        else:
            print(f"✗ Login failed: {response.status_code}")

if __name__ == "__main__":
    print("Testing Role-Based Leave Management System")
    print("==========================================")
    
    # Test basic authentication
    token, employee = test_authentication()
    
    if token:
        test_role_based_endpoints(token, employee)
    
    # Test all roles
    test_different_roles()
