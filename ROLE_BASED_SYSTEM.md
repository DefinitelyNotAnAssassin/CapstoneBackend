# Role-Based Leave Management System

## Implementation Summary

### 1. Employee Role Hierarchy (Academic)
- **Level 0 - VPAA**: Can approve all leave requests
- **Level 1 - Dean**: Can approve requests from their department (except VPAA/Dean level)
- **Level 2 - Program Chair (PC)**: Can approve requests from their program (except VPAA/Dean/PC level)
- **Level 3 - Regular Faculty (RF)**: Cannot approve requests
- **Level 4 - Part-Time Faculty (PTF)**: Cannot approve requests
- **Level 5 - Secretary (SEC)**: Cannot approve requests

### 2. Authentication System
- Employee login with email and default password "sdca2025"
- Token-based authentication for API access
- Employee-to-token mapping for session management

### 3. Role-Based API Endpoints

#### Authentication Endpoints
- `POST /api/auth/login/` - Employee login
- `POST /api/auth/verify-token/` - Token verification
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/demo-login/` - Demo admin login

#### Leave Management Endpoints (Role-Based)
- `GET /api/leave-requests/my_requests/` - Get employee's own leave requests
- `GET /api/leave-requests/pending_for_approval/` - Get requests pending approval (role-based filtering)
- `POST /api/leave-requests/{id}/approve_request/` - Approve leave request (role-based)
- `POST /api/leave-requests/{id}/reject_request/` - Reject leave request (role-based)
- `GET /api/leave-requests/approval_hierarchy/` - Get approval hierarchy for employee

### 4. Role-Based Access Control Logic

#### Approval Scope:
- **VPAA (Level 0)**: All employees
- **Dean (Level 1)**: Employees in same department (Level 2-5)
- **PC (Level 2)**: Employees in same program (Level 3-5)

#### Business Rules:
- Cannot approve requests for employees at same or higher level
- Department-based approval for Deans
- Program-based approval for Program Chairs
- VPAA has universal approval authority

### 5. Test Results
All roles tested successfully:
- ✅ VPAA: Universal approval scope
- ✅ Dean: Department-based approval scope
- ✅ PC: Program-based approval scope
- ✅ Faculty: No approval permissions

### 6. Usage Example

```python
# Login as Program Chair
response = requests.post('/api/auth/login/', {
    "email": "jennifer.davis@university.edu",
    "password": "sdca2025"
})
token = response.json()['token']

# Get pending approvals
headers = {'Authorization': f'Token {token}'}
response = requests.get('/api/leave-requests/pending_for_approval/', headers=headers)

# Approve a request
response = requests.post('/api/leave-requests/1/approve_request/', 
    headers=headers,
    json={"approval_notes": "Approved for academic purposes"}
)
```

### 7. Integration with Frontend

The system is ready for frontend integration with:
- Token-based authentication
- Role-based UI rendering
- Permission-based action availability
- Clear error messages for unauthorized actions

### 8. Security Features

- Password hashing for employee passwords
- Token-based session management
- Role-based authorization checks
- Proper error handling for unauthorized access
