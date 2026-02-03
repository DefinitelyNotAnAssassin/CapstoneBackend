"""
Utility functions for leave_requests app
"""
from datetime import datetime, timedelta


def calculate_business_days(start_date, end_date):
    """
    Calculate business days between two dates.
    Counts Monday to Saturday, excludes Sunday.
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
        # Exclude Sunday (6)
        if current_date.weekday() != 6:  # weekday() returns 0-6 (Mon-Sun)
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days


def get_authenticated_employee(request):
    """Get the authenticated employee from the request"""
    from employees.models import Employee
    from employees.views import TOKEN_STORAGE
    
    print(f"DEBUG: get_authenticated_employee called")
    print(f"DEBUG: Request headers: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
    
    # Check for auth token in headers
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token ') or auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        print(f"DEBUG: Found token: {token[:10]}...")
        print(f"DEBUG: TOKEN_STORAGE keys count: {len(TOKEN_STORAGE)}")
        
        # Get employee ID from token storage
        employee_id = TOKEN_STORAGE.get(token)
        if employee_id:
            try:
                employee = Employee.objects.get(id=employee_id, is_active=True)
                print(f"DEBUG: Found employee from token storage: {employee}")
                return employee
            except Employee.DoesNotExist:
                print(f"DEBUG: Employee with ID {employee_id} not found")
        else:
            print(f"DEBUG: Token not found in storage. Attempting cache lookup...")
            # Try to get from cache (in case server restarted)
            from django.core.cache import cache
            cached_employee_id = cache.get(f'token_{token}')
            if cached_employee_id:
                try:
                    employee = Employee.objects.get(id=cached_employee_id, is_active=True)
                    print(f"DEBUG: Found employee from cache: {employee}")
                    # Re-populate TOKEN_STORAGE
                    TOKEN_STORAGE[token] = cached_employee_id
                    return employee
                except Employee.DoesNotExist:
                    print(f"DEBUG: Cached employee with ID {cached_employee_id} not found")
    
    # Check for employee email in request data (for testing)
    email = None
    if hasattr(request, 'data') and request.data:
        email = request.data.get('employee_email')
    
    # Also check query parameters
    if not email:
        email = request.GET.get('employee_email')
        
    if email:
        try:
            employee = Employee.objects.get(email=email, is_active=True)
            print(f"DEBUG: Found employee by email: {employee}")
            return employee
        except Employee.DoesNotExist:
            print(f"DEBUG: Employee with email {email} not found")
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            employee = Employee.objects.get(user=request.user, is_active=True)
            print(f"DEBUG: Found employee from Django user: {employee}")
            return employee
        except Employee.DoesNotExist:
            print(f"DEBUG: No employee linked to Django user")
    
    print("DEBUG: No authenticated employee found")
    return None
