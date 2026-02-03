from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from employees.models import Employee
from employees.utils import is_hr_employee
from leave_requests.utils import get_authenticated_employee
from .models import LeaveCredit, LeaveBalance
from .serializers import LeaveCreditSerializer, LeaveBalanceSerializer


class LeaveCreditViewSet(viewsets.ModelViewSet):
    queryset = LeaveCredit.objects.select_related('employee').all()
    serializer_class = LeaveCreditSerializer
    
    def get_queryset(self):
        authenticated_employee = get_authenticated_employee(self.request)
        print(f"DEBUG get_queryset: authenticated_employee = {authenticated_employee}")
        print(f"DEBUG get_queryset: is_hr_employee = {is_hr_employee(authenticated_employee) if authenticated_employee else 'N/A'}")
        
        queryset = super().get_queryset()
        print(f"DEBUG get_queryset: Initial queryset count = {queryset.count()}")
        
        employee_id = self.request.query_params.get('employee_id')
        year = self.request.query_params.get('year')
        
        print(f"DEBUG get_queryset: employee_id = {employee_id}, year = {year}")
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
            print(f"DEBUG get_queryset: After employee_id filter count = {queryset.count()}")
        if year:
            queryset = queryset.filter(year=year)
            print(f"DEBUG get_queryset: After year filter count = {queryset.count()}")
        
        print(f"DEBUG get_queryset: Final queryset count = {queryset.count()}")
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_credits(self, request):
        """Get leave credits for the authenticated employee"""
        authenticated_employee = get_authenticated_employee(request)
        if not authenticated_employee:
            return Response({"error": "Authentication required"}, status=401)
        
        credits = self.queryset.filter(employee=authenticated_employee)
        year = request.query_params.get('year')
        if year:
            credits = credits.filter(year=year)
        
        # Filter based on employee's gender
        employee_gender = authenticated_employee.gender
        print("Employee Gender:", employee_gender)
        filtered_credits = []
        
        for credit in credits:
            # Filter maternity leave for females only
            if credit.leave_type == 'Maternity Leave' and employee_gender != 'Female':
                continue
            # Filter paternity leave for males only
            elif credit.leave_type == 'Paternity Leave' and employee_gender != 'Male':
                continue
            else:
                filtered_credits.append(credit)
        
        serializer = self.get_serializer(filtered_credits, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get leave credits by employee ID"""
        employee_id = request.query_params.get('employee_id')
        year = request.query_params.get('year')
        
        if not employee_id:
            return Response({"error": "employee_id parameter required"}, status=400)
        
        # Check if the authenticated employee can view credits for the specified employee
        try:
            target_employee = Employee.objects.get(id=employee_id, is_active=True)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)
        
        credits = self.queryset.filter(employee_id=employee_id)
        if year:
            credits = credits.filter(year=year)
        
        # Filter based on target employee's gender for gender-specific leaves
        employee_gender = target_employee.gender
        filtered_credits = []
        
        for credit in credits:
            # Filter maternity leave for females only
            if credit.leave_type == 'Maternity Leave' and employee_gender != 'Female':
                continue
            # Filter paternity leave for males only
            elif credit.leave_type == 'Paternity Leave' and employee_gender != 'Male':
                continue
            else:
                filtered_credits.append(credit)
        
        serializer = self.get_serializer(filtered_credits, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_year(self, request):
        """Get leave credits by year"""
        year = request.query_params.get('year')
        if year:
            credits = self.queryset.filter(year=year)
            serializer = self.get_serializer(credits, many=True)
            return Response(serializer.data)
        return Response({"error": "year parameter required"}, status=400)

    def create(self, request, *args, **kwargs):
        authenticated_employee = get_authenticated_employee(request)
        print("DEBUG create: Authenticated Employee:", authenticated_employee)
        print("DEBUG create: Is HR Employee:", is_hr_employee(authenticated_employee) if authenticated_employee else 'N/A')
        
        # Log who is creating the leave credit
        employee_email = request.data.get('employee_email')
        if employee_email:
            print(f"Leave credit created by: {employee_email}")
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        authenticated_employee = get_authenticated_employee(request)
        print("Authenticated Employee:", authenticated_employee)
        print("Is HR Employee:", is_hr_employee(authenticated_employee))
        
        # Log who is updating the leave credit
        employee_email = request.data.get('employee_email')
        if employee_email:
            print(f"Leave credit updated by: {employee_email}")
        
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        authenticated_employee = get_authenticated_employee(request)
        print("Authenticated Employee:", authenticated_employee)
        
        # Log who is updating the leave credit
        employee_email = request.data.get('employee_email')
        if employee_email:
            print(f"Leave credit partially updated by: {employee_email}")
        
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        authenticated_employee = get_authenticated_employee(request)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def create_test_data(self, request):
        """Create sample leave credits for testing (DEBUG PURPOSE ONLY)"""
        from datetime import date
        
        # Get all active employees
        employees = Employee.objects.filter(is_active=True)[:5]  # Limit to first 5 employees
        current_year = date.today().year
        
        leave_types = ['Vacation Leave', 'Sick Leave', 'Birthday Leave']
        created_credits = []
        
        for employee in employees:
            for leave_type in leave_types:
                # Check if credit already exists
                credit, created = LeaveCredit.objects.get_or_create(
                    employee=employee,
                    leave_type=leave_type,
                    year=current_year,
                    defaults={
                        'total_credits': 15.0,
                        'used_credits': 0.0,
                        'remaining_credits': 15.0
                    }
                )
                if created:
                    created_credits.append({
                        'employee': employee.full_name,
                        'leave_type': leave_type,
                        'year': current_year,
                        'total_credits': credit.total_credits
                    })
        
        return Response({
            'message': f'Created {len(created_credits)} leave credit records',
            'credits': created_credits
        })

    @action(detail=False, methods=['get'])
    def debug_info(self, request):
        """Debug information about leave credits"""
        total_credits = LeaveCredit.objects.count()
        total_employees = Employee.objects.filter(is_active=True).count()
        
        authenticated_employee = get_authenticated_employee(request)
        is_hr = is_hr_employee(authenticated_employee) if authenticated_employee else False
        
        # Get sample credits
        sample_credits = []
        for credit in LeaveCredit.objects.all()[:5]:
            sample_credits.append({
                'id': credit.id,
                'employee': credit.employee.full_name,
                'leave_type': credit.leave_type,
                'year': credit.year,
                'total_credits': str(credit.total_credits),
                'used_credits': str(credit.used_credits),
                'remaining_credits': str(credit.remaining_credits)
            })
        
        return Response({
            'total_leave_credits': total_credits,
            'total_active_employees': total_employees,
            'authenticated_employee': authenticated_employee.full_name if authenticated_employee else None,
            'is_hr_employee': is_hr,
            'sample_credits': sample_credits,
            'query_params': dict(request.query_params),
            'auth_header': request.META.get('HTTP_AUTHORIZATION', 'No auth header')
        })


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.select_related('employee').all()
    serializer_class = LeaveBalanceSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_balance(self, request):
        """Get leave balances for the authenticated employee"""
        authenticated_employee = get_authenticated_employee(request)
        if not authenticated_employee:
            return Response({"error": "Authentication required"}, status=401)
        
        balances = self.queryset.filter(employee=authenticated_employee)
        
        # Filter based on employee's gender
        employee_gender = authenticated_employee.gender
        filtered_balances = []
        
        for balance in balances:
            # Filter maternity leave for females only
            if balance.leave_type == 'Maternity Leave' and employee_gender != 'Female':
                continue
            # Filter paternity leave for males only
            elif balance.leave_type == 'Paternity Leave' and employee_gender != 'Male':
                continue
            else:
                filtered_balances.append(balance)
        
        serializer = self.get_serializer(filtered_balances, many=True)
        return Response(serializer.data)
