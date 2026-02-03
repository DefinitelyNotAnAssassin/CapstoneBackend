from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from employees.models import Employee
from leave_credits.models import LeaveCredit
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer, LeaveRequestCreateSerializer
from .utils import get_authenticated_employee


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
        else:
            return Response({
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

        # Reformat start_date and end_date to 'YYYY-MM-DD'
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')

        if start_date:
            try:
                request_data['start_date'] = timezone.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                return Response({"error": "Invalid start_date format. Use YYYY-MM-DD."}, status=400)

        if end_date:
            try:
                request_data['end_date'] = timezone.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                return Response({"error": "Invalid end_date format. Use YYYY-MM-DD."}, status=400)
        
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
        """Approve a leave request (role-based) and deduct leave credits from LeaveCredit only"""
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
        
        # Deduct leave credits from LeaveCredit
        from datetime import date
        year = leave_request.start_date.year if hasattr(leave_request, 'start_date') and leave_request.start_date else date.today().year
        try:
            leave_credit = LeaveCredit.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=year
            )
        except LeaveCredit.DoesNotExist:
            return Response({
                "error": f"No leave credit found for {leave_request.leave_type} in {year}"
            }, status=400)
        
        if leave_credit.remaining_credits < leave_request.days_requested:
            return Response({
                "error": "Insufficient leave credits"
            }, status=400)
        
        leave_credit.used_credits += leave_request.days_requested
        leave_credit.save()
        
        # Approve the request
        leave_request.status = 'Approved'
        leave_request.approved_by = employee
        leave_request.approval_date = timezone.now()
        leave_request.approval_notes = approval_notes
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response({
            "message": "Leave request approved successfully. Leave credit updated.",
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
