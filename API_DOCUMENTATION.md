# HRIS API Documentation

This document describes the Django REST Framework API endpoints for the HRIS (Human Resources Information System).

## Base URL
```
http://127.0.0.1:8000/api/
```

## Authentication
Currently configured to allow all requests for development. In production, you should implement proper authentication.

## Organizations API

### Organizations
- **GET** `/api/organizations/` - List all organizations
- **POST** `/api/organizations/` - Create a new organization
- **GET** `/api/organizations/{id}/` - Get specific organization
- **PUT** `/api/organizations/{id}/` - Update organization
- **DELETE** `/api/organizations/{id}/` - Delete organization

### Departments
- **GET** `/api/departments/` - List all departments
- **POST** `/api/departments/` - Create a new department
- **GET** `/api/departments/{id}/` - Get specific department
- **PUT** `/api/departments/{id}/` - Update department
- **DELETE** `/api/departments/{id}/` - Delete department
- **GET** `/api/departments/by_organization/?organization_id={id}` - Get departments by organization

### Programs
- **GET** `/api/programs/` - List all programs
- **POST** `/api/programs/` - Create a new program
- **GET** `/api/programs/{id}/` - Get specific program
- **PUT** `/api/programs/{id}/` - Update program
- **DELETE** `/api/programs/{id}/` - Delete program
- **GET** `/api/programs/by_department/?department_id={id}` - Get programs by department

### Offices
- **GET** `/api/offices/` - List all offices
- **POST** `/api/offices/` - Create a new office
- **GET** `/api/offices/{id}/` - Get specific office
- **PUT** `/api/offices/{id}/` - Update office
- **DELETE** `/api/offices/{id}/` - Delete office
- **GET** `/api/offices/by_department/?department_id={id}` - Get offices by department

### Positions
- **GET** `/api/positions/` - List all positions
- **POST** `/api/positions/` - Create a new position
- **GET** `/api/positions/{id}/` - Get specific position
- **PUT** `/api/positions/{id}/` - Update position
- **DELETE** `/api/positions/{id}/` - Delete position
- **GET** `/api/positions/by_type/?type={Academic|Administration}` - Get positions by type

## Employees API

### Employees
- **GET** `/api/employees/` - List all employees (simplified data)
- **POST** `/api/employees/` - Create a new employee
- **GET** `/api/employees/{id}/` - Get specific employee (full data)
- **PUT** `/api/employees/{id}/` - Update employee
- **DELETE** `/api/employees/{id}/` - Delete employee

### Employee Search & Filters
- **GET** `/api/employees/search/?q={query}` - Search employees by name, ID, or email
- **GET** `/api/employees/by_department/?department_id={id}` - Get employees by department
- **GET** `/api/employees/by_position/?position_id={id}` - Get employees by position
- **GET** `/api/employees/by_status/?is_active={true|false}` - Get employees by status
- **GET** `/api/employees/by_email/?email={email}` - Get employee by email
- **GET** `/api/employees/by_auth_user/?user_id={id}` - Get employee by auth user ID
- **GET** `/api/employees/count/` - Get employee count statistics

### Employee Related Data
- **GET** `/api/employee-education/` - List employee education records
- **POST** `/api/employee-education/` - Create education record
- **GET** `/api/employee-education/?employee_id={id}` - Get education by employee

- **GET** `/api/employee-siblings/` - List employee siblings
- **POST** `/api/employee-siblings/` - Create sibling record
- **GET** `/api/employee-siblings/?employee_id={id}` - Get siblings by employee

- **GET** `/api/employee-dependents/` - List employee dependents
- **POST** `/api/employee-dependents/` - Create dependent record
- **GET** `/api/employee-dependents/?employee_id={id}` - Get dependents by employee

- **GET** `/api/employee-awards/` - List employee awards
- **POST** `/api/employee-awards/` - Create award record
- **GET** `/api/employee-awards/?employee_id={id}` - Get awards by employee

- **GET** `/api/employee-licenses/` - List employee licenses
- **POST** `/api/employee-licenses/` - Create license record
- **GET** `/api/employee-licenses/?employee_id={id}` - Get licenses by employee

- **GET** `/api/employee-schedules/` - List employee schedules
- **POST** `/api/employee-schedules/` - Create schedule record
- **GET** `/api/employee-schedules/?employee_id={id}` - Get schedules by employee

## Leave Management API

### Leave Policies
- **GET** `/api/leave-policies/` - List all leave policies
- **POST** `/api/leave-policies/` - Create a new leave policy
- **GET** `/api/leave-policies/{id}/` - Get specific leave policy
- **PUT** `/api/leave-policies/{id}/` - Update leave policy
- **DELETE** `/api/leave-policies/{id}/` - Delete leave policy

### Leave Requests
- **GET** `/api/leave-requests/` - List all leave requests
- **POST** `/api/leave-requests/` - Create a new leave request
- **GET** `/api/leave-requests/{id}/` - Get specific leave request
- **PUT** `/api/leave-requests/{id}/` - Update leave request
- **DELETE** `/api/leave-requests/{id}/` - Delete leave request

### Leave Request Actions
- **GET** `/api/leave-requests/by_employee/?employee_id={id}` - Get leave requests by employee
- **GET** `/api/leave-requests/by_status/?status={Pending|Approved|Rejected|Cancelled}` - Get leave requests by status
- **GET** `/api/leave-requests/pending_approvals/` - Get all pending leave requests
- **POST** `/api/leave-requests/{id}/approve/` - Approve a leave request
- **POST** `/api/leave-requests/{id}/reject/` - Reject a leave request

### Leave Credits
- **GET** `/api/leave-credits/` - List all leave credits
- **POST** `/api/leave-credits/` - Create leave credit record
- **GET** `/api/leave-credits/by_employee/?employee_id={id}` - Get leave credits by employee
- **GET** `/api/leave-credits/by_employee/?employee_id={id}&year={year}` - Get leave credits by employee and year
- **GET** `/api/leave-credits/by_year/?year={year}` - Get leave credits by year

### Leave Balances
- **GET** `/api/leave-balances/` - List all leave balances
- **POST** `/api/leave-balances/` - Create leave balance record
- **GET** `/api/leave-balances/by_employee/?employee_id={id}` - Get leave balances by employee

## Data Models

### Employee Creation Format
```json
{
  "employee_id": "EMP001",
  "first_name": "John",
  "middle_name": "Michael",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "password123",
  "present_address": "123 Main St",
  "mobile_no": "09123456789",
  "birth_date": "1990-01-01",
  "birth_place": "Manila",
  "age": 34,
  "gender": "Male",
  "citizenship": "Filipino",
  "civil_status": "Single",
  "date_hired": "2024-01-01",
  "position": 1,
  "department": 1,
  "office": 1,
  "program": 1,
  "additional_education": [
    {
      "degree": "Bachelor",
      "school": "University of Manila",
      "course": "Computer Science",
      "year": "2012"
    }
  ]
}
```

### Response Format
All list endpoints return paginated data:
```json
{
  "count": 100,
  "next": "http://127.0.0.1:8000/api/employees/?page=2",
  "previous": null,
  "results": [...]
}
```

## Database Setup

To set up the database with sample data:

1. Run migrations:
```bash
py manage.py migrate
```

2. Populate with sample organization data:
```bash
py manage.py populate_org_data
```

## CORS Configuration

The API is configured to accept requests from:
- http://localhost:3000
- http://localhost:8100
- http://127.0.0.1:3000
- http://127.0.0.1:8100

## Notes

- All date fields use ISO format (YYYY-MM-DD)
- Employee passwords are handled securely and never returned in API responses
- The API creates Django User accounts automatically when employees are created with passwords
- Foreign key relationships are handled by ID numbers
- The API supports full CRUD operations on all models
- Error responses include detailed error messages
- File uploads for employee photos and documents are supported via the profile_image field and supporting_documents fields
