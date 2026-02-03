"""
RBAC Views

API endpoints for Role-Based Access Control management.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count
from django.db import transaction
from django.utils import timezone

from .models import Permission, Role, RolePermission, EmployeeRole, PermissionModule, RBACChangeLog
from .serializers import (
    PermissionSerializer, PermissionListSerializer,
    RoleSerializer, RoleListSerializer, RoleCreateUpdateSerializer,
    RolePermissionSerializer,
    EmployeeRoleSerializer, EmployeeRoleCreateSerializer,
    PermissionModuleSerializer,
    RBACChangeLogSerializer,
    EmployeePermissionsSerializer,
    BulkRoleAssignmentSerializer
)
from employees.models import Employee


def log_rbac_change(action, model_type, model_id, performed_by=None, 
                    previous_value=None, new_value=None, affected_employee=None,
                    ip_address=None, user_agent='', notes=''):
    """Helper function to create RBAC change logs"""
    RBACChangeLog.objects.create(
        action=action,
        model_type=model_type,
        model_id=model_id,
        performed_by=performed_by,
        previous_value=previous_value,
        new_value=new_value,
        affected_employee=affected_employee,
        ip_address=ip_address,
        user_agent=user_agent,
        notes=notes
    )


def get_employee_from_request(request):
    """Extract employee from request based on auth token or email header"""
    # Try to get employee from request user
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            return Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            pass
    
    # Try email header (for API calls)
    email = request.headers.get('X-Employee-Email')
    if email:
        try:
            return Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            pass
    
    return None


class PermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Permissions.
    
    Endpoints:
    - GET /permissions/ - List all permissions
    - POST /permissions/ - Create a new permission
    - GET /permissions/{id}/ - Retrieve a permission
    - PUT /permissions/{id}/ - Update a permission
    - DELETE /permissions/{id}/ - Delete a permission (non-system only)
    - GET /permissions/by_category/ - List permissions grouped by category
    """
    
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'category', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PermissionListSerializer
        return PermissionSerializer
    
    def perform_create(self, serializer):
        permission = serializer.save()
        employee = get_employee_from_request(self.request)
        log_rbac_change(
            'create', 'permission', permission.id,
            performed_by=employee,
            new_value={'code': permission.code, 'name': permission.name}
        )
    
    def perform_update(self, serializer):
        old_data = {'code': self.get_object().code, 'name': self.get_object().name}
        permission = serializer.save()
        employee = get_employee_from_request(self.request)
        log_rbac_change(
            'update', 'permission', permission.id,
            performed_by=employee,
            previous_value=old_data,
            new_value={'code': permission.code, 'name': permission.name}
        )
    
    def destroy(self, request, *args, **kwargs):
        permission = self.get_object()
        if permission.is_system:
            return Response(
                {'error': 'System permissions cannot be deleted'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        employee = get_employee_from_request(request)
        log_rbac_change(
            'delete', 'permission', permission.id,
            performed_by=employee,
            previous_value={'code': permission.code, 'name': permission.name}
        )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get permissions grouped by category"""
        categories = {}
        for permission in self.get_queryset().filter(is_active=True):
            cat = permission.category
            if cat not in categories:
                categories[cat] = {
                    'category': cat,
                    'category_display': permission.get_category_display(),
                    'permissions': []
                }
            categories[cat]['permissions'].append(
                PermissionListSerializer(permission).data
            )
        
        return Response(list(categories.values()))
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active permissions"""
        permissions = self.get_queryset().filter(is_active=True)
        serializer = PermissionListSerializer(permissions, many=True)
        return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Roles.
    
    Endpoints:
    - GET /roles/ - List all roles
    - POST /roles/ - Create a new role
    - GET /roles/{id}/ - Retrieve a role with permissions
    - PUT /roles/{id}/ - Update a role
    - DELETE /roles/{id}/ - Delete a role (non-system only)
    - POST /roles/{id}/permissions/ - Add permissions to role
    - DELETE /roles/{id}/permissions/{perm_id}/ - Remove permission from role
    - GET /roles/{id}/employees/ - List employees with this role
    """
    
    queryset = Role.objects.prefetch_related(
        'role_permissions__permission',
        'employee_assignments'
    ).all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'level', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RoleCreateUpdateSerializer
        return RoleSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request_employee'] = get_employee_from_request(self.request)
        return context
    
    def perform_create(self, serializer):
        employee = get_employee_from_request(self.request)
        role = serializer.save(created_by=employee)
        log_rbac_change(
            'create', 'role', role.id,
            performed_by=employee,
            new_value={'code': role.code, 'name': role.name, 'level': role.level}
        )
    
    def perform_update(self, serializer):
        role = self.get_object()
        old_data = {'code': role.code, 'name': role.name, 'level': role.level}
        role = serializer.save()
        employee = get_employee_from_request(self.request)
        log_rbac_change(
            'update', 'role', role.id,
            performed_by=employee,
            previous_value=old_data,
            new_value={'code': role.code, 'name': role.name, 'level': role.level}
        )
    
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        if role.is_system:
            return Response(
                {'error': 'System roles cannot be deleted'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if role has active assignments
        if role.employee_assignments.filter(is_active=True).exists():
            return Response(
                {'error': 'Cannot delete role with active employee assignments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employee = get_employee_from_request(request)
        log_rbac_change(
            'delete', 'role', role.id,
            performed_by=employee,
            previous_value={'code': role.code, 'name': role.name}
        )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        """Add a permission to this role"""
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        if not permission_id:
            return Response(
                {'error': 'permission_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            permission = Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return Response(
                {'error': 'Permission not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        employee = get_employee_from_request(request)
        rp, created = RolePermission.objects.get_or_create(
            role=role,
            permission=permission,
            defaults={'granted_by': employee}
        )
        
        if created:
            log_rbac_change(
                'grant', 'role_permission', rp.id,
                performed_by=employee,
                new_value={'role': role.code, 'permission': permission.code}
            )
        
        return Response(
            {'message': 'Permission added' if created else 'Permission already exists'},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['delete'], url_path='remove_permission/(?P<permission_id>[0-9]+)')
    def remove_permission(self, request, pk=None, permission_id=None):
        """Remove a permission from this role"""
        role = self.get_object()
        
        try:
            rp = RolePermission.objects.get(role=role, permission_id=permission_id)
        except RolePermission.DoesNotExist:
            return Response(
                {'error': 'Role does not have this permission'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        employee = get_employee_from_request(request)
        log_rbac_change(
            'deny', 'role_permission', rp.id,
            performed_by=employee,
            previous_value={'role': role.code, 'permission': rp.permission.code}
        )
        rp.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """List employees with this role"""
        role = self.get_object()
        assignments = role.employee_assignments.filter(is_active=True).select_related(
            'employee', 'department_scope', 'program_scope'
        )
        serializer = EmployeeRoleSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def assignable(self, request):
        """Get roles that can be assigned to employees"""
        roles = self.get_queryset().filter(is_active=True, can_be_assigned=True)
        serializer = RoleListSerializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a role with a new name"""
        original = self.get_object()
        new_name = request.data.get('name')
        new_code = request.data.get('code')
        
        if not new_name or not new_code:
            return Response(
                {'error': 'name and code are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employee = get_employee_from_request(request)
        
        with transaction.atomic():
            new_role = Role.objects.create(
                name=new_name,
                code=new_code,
                description=f"Copied from {original.name}\n\n{original.description}",
                level=original.level,
                approval_scope=original.approval_scope,
                is_system=False,
                is_active=True,
                can_be_assigned=True,
                created_by=employee
            )
            
            # Copy permissions
            for rp in original.role_permissions.filter(is_active=True):
                RolePermission.objects.create(
                    role=new_role,
                    permission=rp.permission,
                    conditions=rp.conditions,
                    granted_by=employee
                )
            
            log_rbac_change(
                'create', 'role', new_role.id,
                performed_by=employee,
                new_value={'code': new_role.code, 'copied_from': original.code}
            )
        
        serializer = RoleSerializer(new_role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmployeeRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Employee Role assignments.
    
    Endpoints:
    - GET /employee-roles/ - List all role assignments
    - POST /employee-roles/ - Assign a role to an employee
    - GET /employee-roles/{id}/ - Retrieve an assignment
    - PUT /employee-roles/{id}/ - Update an assignment
    - DELETE /employee-roles/{id}/ - Remove an assignment
    - GET /employee-roles/by_employee/{employee_id}/ - Get roles for an employee
    - POST /employee-roles/bulk_assign/ - Bulk assign roles
    """
    
    queryset = EmployeeRole.objects.select_related(
        'employee', 'role', 'department_scope', 'program_scope', 'assigned_by'
    ).all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['employee__first_name', 'employee__last_name', 'role__name']
    ordering_fields = ['assigned_at', 'role__level', 'is_primary']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EmployeeRoleCreateSerializer
        return EmployeeRoleSerializer
    
    def perform_create(self, serializer):
        employee = get_employee_from_request(self.request)
        assignment = serializer.save(assigned_by=employee)
        
        log_rbac_change(
            'assign', 'employee_role', assignment.id,
            performed_by=employee,
            affected_employee=assignment.employee,
            new_value={
                'role': assignment.role.code,
                'is_primary': assignment.is_primary
            }
        )
    
    def perform_destroy(self, instance):
        employee = get_employee_from_request(self.request)
        log_rbac_change(
            'revoke', 'employee_role', instance.id,
            performed_by=employee,
            affected_employee=instance.employee,
            previous_value={
                'role': instance.role.code,
                'is_primary': instance.is_primary
            }
        )
        instance.delete()
    
    @action(detail=False, methods=['get'], url_path='by_employee/(?P<employee_id>[0-9]+)')
    def by_employee(self, request, employee_id=None):
        """Get all roles for a specific employee"""
        assignments = self.get_queryset().filter(
            employee_id=employee_id,
            is_active=True
        )
        serializer = EmployeeRoleSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        """Bulk assign a role to multiple employees"""
        serializer = BulkRoleAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        employee_ids = data['employee_ids']
        role_id = data['role_id']
        
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        current_employee = get_employee_from_request(request)
        created = []
        errors = []
        
        with transaction.atomic():
            for emp_id in employee_ids:
                try:
                    employee = Employee.objects.get(id=emp_id)
                    assignment, was_created = EmployeeRole.objects.get_or_create(
                        employee=employee,
                        role=role,
                        department_scope_id=data.get('department_scope'),
                        program_scope_id=data.get('program_scope'),
                        defaults={
                            'is_primary': data.get('is_primary', False),
                            'valid_from': data.get('valid_from'),
                            'valid_until': data.get('valid_until'),
                            'notes': data.get('notes', ''),
                            'assigned_by': current_employee
                        }
                    )
                    
                    if was_created:
                        created.append(emp_id)
                        log_rbac_change(
                            'assign', 'employee_role', assignment.id,
                            performed_by=current_employee,
                            affected_employee=employee,
                            new_value={'role': role.code}
                        )
                except Employee.DoesNotExist:
                    errors.append({'employee_id': emp_id, 'error': 'Employee not found'})
                except Exception as e:
                    errors.append({'employee_id': emp_id, 'error': str(e)})
        
        return Response({
            'created': len(created),
            'created_ids': created,
            'errors': errors
        })
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set this role assignment as the primary for the employee"""
        assignment = self.get_object()
        
        # Remove primary from other assignments
        EmployeeRole.objects.filter(
            employee=assignment.employee,
            is_primary=True
        ).exclude(pk=assignment.pk).update(is_primary=False)
        
        assignment.is_primary = True
        assignment.save()
        
        serializer = EmployeeRoleSerializer(assignment)
        return Response(serializer.data)


class PermissionModuleViewSet(viewsets.ModelViewSet):
    """ViewSet for Permission Modules"""
    
    queryset = PermissionModule.objects.prefetch_related('permissions').all()
    serializer_class = PermissionModuleSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'name']


class RBACChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for RBAC Change Logs (read-only)"""
    
    queryset = RBACChangeLog.objects.select_related(
        'performed_by', 'affected_employee'
    ).all()
    serializer_class = RBACChangeLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['notes', 'performed_by__first_name', 'performed_by__last_name']
    ordering_fields = ['performed_at', 'action', 'model_type']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(performed_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(performed_at__date__lte=end_date)
        
        # Filter by action type
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by affected employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(affected_employee_id=employee_id)
        
        return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employee_permissions(request, employee_id):
    """
    Get the complete permissions profile for an employee.
    This is the main endpoint used by the frontend RoleContext.
    
    Returns:
    - Primary role information
    - All role assignments
    - Effective permissions (merged from all roles)
    - Approval scope and level
    """
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get all valid role assignments
    role_assignments = EmployeeRole.objects.filter(
        employee=employee,
        is_active=True,
        role__is_active=True
    ).select_related('role', 'department_scope', 'program_scope')
    
    # Filter to currently valid assignments
    valid_assignments = [a for a in role_assignments if a.is_valid()]
    
    # Determine primary role
    primary_assignment = next(
        (a for a in valid_assignments if a.is_primary),
        valid_assignments[0] if valid_assignments else None
    )
    
    # Collect all permissions from all roles
    all_permissions = set()
    for assignment in valid_assignments:
        perms = assignment.role.get_all_permissions()
        all_permissions.update(perms)
    
    # Determine highest authority level (lowest number)
    highest_level = min(
        (a.role.level for a in valid_assignments),
        default=99
    )
    
    # Determine broadest approval scope
    scope_hierarchy = ['all', 'organization', 'department', 'program', 'none']
    approval_scope = 'none'
    for assignment in valid_assignments:
        scope = assignment.role.approval_scope
        if scope_hierarchy.index(scope) < scope_hierarchy.index(approval_scope):
            approval_scope = scope
    
    # Check if employee is HR (has all permissions or special HR role)
    is_hr = 'hr_full_access' in all_permissions or highest_level == -1
    
    # Can approve if has any approval-related permissions
    can_approve = any(p.startswith('can_approve') or p == 'leave_approve' for p in all_permissions)
    
    response_data = {
        'employee_id': employee.id,
        'employee_name': employee.full_name,
        'primary_role': {
            'id': primary_assignment.role.id,
            'name': primary_assignment.role.name,
            'code': primary_assignment.role.code,
            'level': primary_assignment.role.level,
            'approval_scope': primary_assignment.role.approval_scope
        } if primary_assignment else None,
        'all_roles': [
            {
                'id': a.role.id,
                'name': a.role.name,
                'code': a.role.code,
                'level': a.role.level,
                'is_primary': a.is_primary,
                'department_scope': a.department_scope.name if a.department_scope else None,
                'program_scope': a.program_scope.name if a.program_scope else None
            }
            for a in valid_assignments
        ],
        'effective_permissions': sorted(list(all_permissions)),
        'highest_level': highest_level,
        'approval_scope': approval_scope,
        'is_hr': is_hr,
        'can_approve': can_approve
    }
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employee_permissions_by_email(request):
    """
    Get permissions by employee email.
    Useful when the employee ID is not known.
    """
    email = request.query_params.get('email')
    if not email:
        return Response(
            {'error': 'email parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        employee = Employee.objects.get(email=email)
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Reuse the same logic
    return get_employee_permissions(request._request, employee.id)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_permission(request):
    """
    Check if an employee has a specific permission.
    
    Request body:
    {
        "employee_id": 123,
        "permission_code": "can_approve_leave"
    }
    """
    employee_id = request.data.get('employee_id')
    permission_code = request.data.get('permission_code')
    
    if not employee_id or not permission_code:
        return Response(
            {'error': 'employee_id and permission_code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get employee's valid roles
    valid_roles = EmployeeRole.objects.filter(
        employee_id=employee_id,
        is_active=True,
        role__is_active=True
    ).select_related('role')
    
    # Check if any role has the permission
    for assignment in valid_roles:
        if not assignment.is_valid():
            continue
        if assignment.role.has_permission(permission_code):
            return Response({
                'has_permission': True,
                'granted_by_role': assignment.role.code
            })
    
    return Response({'has_permission': False})


@api_view(['GET'])
@permission_classes([AllowAny])
def rbac_stats(request):
    """Get RBAC system statistics for dashboard"""
    return Response({
        'total_permissions': Permission.objects.filter(is_active=True).count(),
        'total_roles': Role.objects.filter(is_active=True).count(),
        'total_assignments': EmployeeRole.objects.filter(is_active=True).count(),
        'system_roles': Role.objects.filter(is_system=True).count(),
        'recent_changes': RBACChangeLog.objects.count(),
        'roles_by_level': list(
            Role.objects.filter(is_active=True)
            .values('level')
            .annotate(count=Count('id'))
            .order_by('level')
        )
    })
