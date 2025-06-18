# Utility functions for employees

def is_hr_employee(employee):
    """Check if an employee belongs to HR department"""
    print(f"DEBUG is_hr_employee: Checking employee: {employee}")
    print(f"DEBUG is_hr_employee: Employee type: {type(employee)}")
    
    if not employee:
        print("DEBUG is_hr_employee: No employee provided")
        return False
    
    if not hasattr(employee, 'department') or not employee.department:
        print("DEBUG is_hr_employee: Employee has no department")
        return False
    
    department_name = employee.department.name
    print(f"DEBUG is_hr_employee: Department name: '{department_name}'")
    
    hr_department_names = [
        'human resources', 'hr', 'hr department', 'hr main office',
        'human resource', 'human resources department'
    ]
    
    is_hr = department_name.strip().lower() in hr_department_names
    print(f"DEBUG is_hr_employee: Is HR employee: {is_hr}")
    
    return is_hr
