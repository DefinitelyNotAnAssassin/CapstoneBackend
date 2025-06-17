from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from employees.models import Employee
from .models import LeavePolicy, LeaveRequest, LeaveCredit, LeaveBalance
from .serializers import (
    LeavePolicySerializer, LeaveRequestSerializer, LeaveRequestCreateSerializer,
    LeaveCreditSerializer, LeaveBalanceSerializer
)


# Import token storage from employees views
from employees.views import TOKEN_STORAGE

# Custom authentication helper
def get_authenticated_employee(request):
    """Get the authenticated employee from the request"""
    print(f"DEBUG: get_authenticated_employee called")
    print(f"DEBUG: Request headers: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
    
    # Check for auth token in headers
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token = auth_header.split(' ')[1]
        print(f"DEBUG: Found token: {token[:10]}...")
        print(f"DEBUG: TOKEN_STORAGE contents: {list(TOKEN_STORAGE.keys())}")
        
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
            print(f"DEBUG: Token not found in storage")
    
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
    
    # Fallback: check if user is authenticated via Django auth
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            employee = Employee.objects.get(user=request.user, is_active=True)
            print(f"DEBUG: Found employee from Django user: {employee}")
            return employee
        except Employee.DoesNotExist:
            print(f"DEBUG: No employee linked to Django user")
    
    print("DEBUG: No authenticated employee found")
    return None


class LeavePolicyViewSet(viewsets.ModelViewSet):
    queryset = LeavePolicy.objects.all()
    serializer_class = LeavePolicySerializer


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee', 'approved_by').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveRequestCreateSerializer
        return LeaveRequestSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a leave request with proper authentication and permission checks"""
        authenticated_employee = get_authenticated_employee(request)
        if not authenticated_employee:
            return Response({"error": "Authentication required"}, status=401)
        
        # Get the target employee from the request data
        target_employee_id = request.data.get('employee')
        if not target_employee_id:
            return Response({"error": "Employee ID is required"}, status=400)
        
        try:
            target_employee = Employee.objects.get(id=target_employee_id, is_active=True)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)
        
        # Check permissions: users can create requests for themselves, or if they have approval authority
        if (authenticated_employee.id == target_employee.id or 
            authenticated_employee.can_approve_for_employee(target_employee)):
            
            # Continue with the standard creation process
            return super().create(request, *args, **kwargs)
        else:            return Response({
                "error": "You don't have permission to create leave requests for this employee"
            }, status=403)
    
    @action(detail=False, methods=['post'])
    def create_my_request(self, request):
        """Create a leave request for the authenticated employee"""
        authenticated_employee = get_authenticated_employee(request)
        if not authenticated_employee:
            return Response({"error": "Authentication required"}, status=401)
          # Add the authenticated employee to the request data
        request_data = request.data.copy()
        request_data['employee'] = authenticated_employee.id
        
        serializer = LeaveRequestCreateSerializer(data=request_data)
        if serializer.is_valid():
            leave_request = serializer.save()
            response_serializer = LeaveRequestSerializer(leave_request)
            return Response({
                "message": "Leave request created successfully",
                "request": response_serializer.data
            }, status=201)
        else:
            return Response(serializer.errors, status=400)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get leave requests for the authenticated employee"""
        authenticated_employee = get_authenticated_employee(request)
        if not authenticated_employee:
            return Response({"error": "Authentication required"}, status=401)        
        requests = self.queryset.filter(employee=authenticated_employee)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_for_approval(self, request):
        """Get leave requests that the authenticated employee can approve"""
        employee = get_authenticated_employee(request)
        
        if not employee:
            return Response({"error": "Authentication required"}, status=401)
        
        # Check approval permissions
        if not employee.can_approve_leaves:
            return Response({"error": "You don't have permission to approve leave requests"}, status=403)
        
        # Get pending requests that this employee can approve
        pending_requests = self.queryset.filter(status='Pending')
        
        # Filter based on approval scope
        scope = employee.approval_scope
        if scope == 'all':
            # VPAA can approve all requests
            requests = pending_requests
        elif scope == 'department':
            # Dean can approve requests from their department (except equal/higher level positions)
            requests = pending_requests.filter(
                employee__department=employee.department
            ).exclude(
                Q(employee__position__rank='VPAA') | 
                Q(employee__position__rank='DEAN')
            )
        elif scope == 'program':
            # PC can approve requests from their program (except equal/higher level positions)
            requests = pending_requests.filter(
                employee__program=employee.program
            ).exclude(
                Q(employee__position__rank='VPAA') | 
                Q(employee__position__rank='DEAN') | 
                Q(employee__position__rank='PC')
            )
        else:
            requests = LeaveRequest.objects.none()
        
        serializer = self.get_serializer(requests, many=True)
        return Response({
            "requests": serializer.data,
            "approver_info": {
                "name": employee.full_name,
                "position": employee.position.title if employee.position else "",
                "role_level": employee.academic_role_level,
                "approval_scope": scope
            }
        })
    
    @action(detail=True, methods=['post'])
    def approve_request(self, request, pk=None):
        """Approve a leave request (role-based)"""
        employee = get_authenticated_employee(request)
        if not employee:
            return Response({"error": "Authentication required"}, status=401)
        
        leave_request = self.get_object()
        approval_notes = request.data.get('approval_notes', '')
        
        # Check if the employee can approve this specific request
        if not employee.can_approve_for_employee(leave_request.employee):
            return Response({
                "error": "You don't have permission to approve this leave request"
            }, status=403)
        
        if leave_request.status != 'Pending':
            return Response({
                "error": f"Cannot approve request with status: {leave_request.status}"
            }, status=400)
        
        # Approve the request
        leave_request.status = 'Approved'
        leave_request.approved_by = employee
        leave_request.approval_date = timezone.now()
        leave_request.approval_notes = approval_notes
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response({
            "message": "Leave request approved successfully",
            "request": serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        """Reject a leave request (role-based)"""
        employee = get_authenticated_employee(request)
        if not employee:
            return Response({"error": "Authentication required"}, status=401)
        
        leave_request = self.get_object()
        approval_notes = request.data.get('approval_notes', '')
        
        # Check if the employee can approve/reject this specific request
        if not employee.can_approve_for_employee(leave_request.employee):
            return Response({
                "error": "You don't have permission to reject this leave request"
            }, status=403)
        
        if leave_request.status != 'Pending':
            return Response({
                "error": f"Cannot reject request with status: {leave_request.status}"
            }, status=400)
        
        if not approval_notes:
            return Response({
                "error": "Rejection reason is required in approval_notes"
            }, status=400)        
        # Reject the request
        leave_request.status = 'Rejected'
        leave_request.approved_by = employee
        leave_request.approval_date = timezone.now()
        leave_request.approval_notes = approval_notes
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response({
            "message": "Leave request rejected",
            "request": serializer.data
        })

    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get leave requests by employee ID"""
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response({"error": "employee_id parameter required"}, status=400)
        
        # Get the authenticated employee for permission checks
        authenticated_employee = get_authenticated_employee(request)
        if not authenticated_employee:
            return Response({"error": "Authentication required"}, status=401)
        
        # Check if the authenticated employee can view requests for the specified employee
        try:
            target_employee = Employee.objects.get(id=employee_id, is_active=True)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)
        
        # Allow viewing own requests or if user has approval permissions for the target employee
        if (authenticated_employee.id == target_employee.id or 
            authenticated_employee.can_approve_for_employee(target_employee)):
            requests = self.queryset.filter(employee=target_employee)
            serializer = self.get_serializer(requests, many=True)
            return Response(serializer.data)
        else:
            return Response({
                "error": "You don't have permission to view this employee's leave requests"
            }, status=403)

    @action(detail=False, methods=['get'])
    def approval_hierarchy(self, request):
        """Get the approval hierarchy for the authenticated employee"""
        employee = get_authenticated_employee(request)
        if not employee:
            return Response({"error": "Authentication required"}, status=401)
        
        # Find who can approve this employee's requests
        potential_approvers = []
        
        if employee.academic_role_level is not None:
            # Get employees who can approve for this employee
            all_employees = Employee.objects.filter(
                is_active=True,
                position__type='Academic'
            ).select_related('position', 'department', 'program')
            
            for approver in all_employees:
                if approver.can_approve_for_employee(employee):
                    potential_approvers.append({
                        "id": approver.id,
                        "name": approver.full_name,
                        "position": approver.position.title if approver.position else "",
                        "department": approver.department.name if approver.department else "",
                        "role_level": approver.academic_role_level,
                        "approval_scope": approver.approval_scope
                    })
        
        return Response({
            "employee": {
                "name": employee.full_name,
                "position": employee.position.title if employee.position else "",
                "role_level": employee.academic_role_level
            },
            "potential_approvers": potential_approvers
        })


class LeaveCreditViewSet(viewsets.ModelViewSet):
    queryset = LeaveCredit.objects.select_related('employee').all()
    serializer_class = LeaveCreditSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee_id')
        year = self.request.query_params.get('year')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if year:
            queryset = queryset.filter(year=year)
            
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
        print("Employee Gender:" , employee_gender)
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
        
        if employee_id:
            credits = self.queryset.filter(employee_id=employee_id)
            if year:
                credits = credits.filter(year=year)
            serializer = self.get_serializer(credits, many=True)
            return Response(serializer.data)
        return Response({"error": "employee_id parameter required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_year(self, request):
        """Get leave credits by year"""
        year = request.query_params.get('year')
        if year:
            credits = self.queryset.filter(year=year)
            serializer = self.get_serializer(credits, many=True)
            return Response(serializer.data)
        return Response({"error": "year parameter required"}, status=400)


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.select_related('employee').all()
    serializer_class = LeaveBalanceSerializer
    
    @action(detail=False, methods=['get'])
    def my_balances(self, request):
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
    
    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get leave balances by employee ID"""
        employee_id = request.query_params.get('employee_id')
        if employee_id:
            balances = self.queryset.filter(employee_id=employee_id)
            serializer = self.get_serializer(balances, many=True)
            return Response(serializer.data)
        return Response({"error": "employee_id parameter required"}, status=400)
