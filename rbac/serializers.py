"""
RBAC Serializers

Serializers for Role-Based Access Control API endpoints.
"""

from rest_framework import serializers
from .models import Permission, Role, RolePermission, EmployeeRole, PermissionModule, RBACChangeLog


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Permission
        fields = [
            'id', 'code', 'name', 'description', 'category', 'category_display',
            'is_system', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PermissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for permission lists"""
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'category', 'is_active']


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for RolePermission through model"""
    
    permission_code = serializers.CharField(source='permission.code', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_category = serializers.CharField(source='permission.category', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'permission', 'permission_code', 'permission_name',
            'permission_category', 'is_active', 'conditions', 'granted_at', 'granted_by'
        ]
        read_only_fields = ['id', 'granted_at']


class RoleSerializer(serializers.ModelSerializer):
    """Full serializer for Role model with nested permissions"""
    
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    approval_scope_display = serializers.CharField(source='get_approval_scope_display', read_only=True)
    permissions_list = PermissionListSerializer(source='permissions', many=True, read_only=True)
    permission_codes = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description', 'level', 'level_display',
            'approval_scope', 'approval_scope_display', 'is_system', 'is_active',
            'can_be_assigned', 'permissions_list', 'permission_codes', 'employee_count',
            'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_permission_codes(self, obj):
        """Get list of permission codes for this role"""
        return obj.get_all_permissions()
    
    def get_employee_count(self, obj):
        """Count active employees with this role"""
        return obj.employee_assignments.filter(is_active=True).count()


class RoleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for role lists"""
    
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    approval_scope_display = serializers.CharField(source='get_approval_scope_display', read_only=True)
    employee_count = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'level', 'level_display', 'approval_scope',
            'approval_scope_display', 'is_system', 'is_active', 'can_be_assigned',
            'employee_count', 'permission_count'
        ]
    
    def get_employee_count(self, obj):
        return obj.employee_assignments.filter(is_active=True).count()
    
    def get_permission_count(self, obj):
        return obj.role_permissions.filter(is_active=True).count()


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating roles"""
    
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description', 'level', 'approval_scope',
            'is_system', 'is_active', 'can_be_assigned', 'permission_ids'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        # Add permissions
        for perm_id in permission_ids:
            RolePermission.objects.create(
                role=role,
                permission_id=perm_id,
                granted_by=self.context.get('request_employee')
            )
        
        return role
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        
        # Update role fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update permissions if provided
        if permission_ids is not None:
            # Remove existing permissions
            instance.role_permissions.all().delete()
            
            # Add new permissions
            for perm_id in permission_ids:
                RolePermission.objects.create(
                    role=instance,
                    permission_id=perm_id,
                    granted_by=self.context.get('request_employee')
                )
        
        return instance


class EmployeeRoleSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeRole assignments"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_code = serializers.CharField(source='role.code', read_only=True)
    role_level = serializers.IntegerField(source='role.level', read_only=True)
    department_scope_name = serializers.CharField(source='department_scope.name', read_only=True)
    program_scope_name = serializers.CharField(source='program_scope.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True)
    is_currently_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeRole
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'employee_email',
            'role', 'role_name', 'role_code', 'role_level',
            'department_scope', 'department_scope_name',
            'program_scope', 'program_scope_name',
            'is_primary', 'is_active', 'valid_from', 'valid_until',
            'is_currently_valid', 'assigned_at', 'assigned_by', 'assigned_by_name', 'notes'
        ]
        read_only_fields = ['id', 'assigned_at']
    
    def get_is_currently_valid(self, obj):
        return obj.is_valid()


class EmployeeRoleCreateSerializer(serializers.ModelSerializer):
    """Serializer for assigning roles to employees"""
    
    class Meta:
        model = EmployeeRole
        fields = [
            'employee', 'role', 'department_scope', 'program_scope',
            'is_primary', 'is_active', 'valid_from', 'valid_until', 'notes'
        ]
    
    def validate(self, data):
        # Check for duplicate assignment
        employee = data.get('employee')
        role = data.get('role')
        dept_scope = data.get('department_scope')
        prog_scope = data.get('program_scope')
        
        existing = EmployeeRole.objects.filter(
            employee=employee,
            role=role,
            department_scope=dept_scope,
            program_scope=prog_scope
        )
        
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError(
                "This employee already has this role with the same scope."
            )
        
        return data


class PermissionModuleSerializer(serializers.ModelSerializer):
    """Serializer for PermissionModule"""
    
    permissions = PermissionListSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = PermissionModule
        fields = [
            'id', 'name', 'code', 'description', 'icon', 'order',
            'is_active', 'permissions', 'permission_ids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        module = PermissionModule.objects.create(**validated_data)
        
        if permission_ids:
            module.permissions.set(permission_ids)
        
        return module
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permission_ids is not None:
            instance.permissions.set(permission_ids)
        
        return instance


class RBACChangeLogSerializer(serializers.ModelSerializer):
    """Serializer for RBAC change logs"""
    
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    model_type_display = serializers.CharField(source='get_model_type_display', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.full_name', read_only=True)
    affected_employee_name = serializers.CharField(source='affected_employee.full_name', read_only=True)
    
    class Meta:
        model = RBACChangeLog
        fields = [
            'id', 'action', 'action_display', 'model_type', 'model_type_display',
            'model_id', 'previous_value', 'new_value', 'performed_by',
            'performed_by_name', 'performed_at', 'ip_address', 'user_agent',
            'affected_employee', 'affected_employee_name', 'notes'
        ]
        read_only_fields = ['id', 'performed_at']


class EmployeePermissionsSerializer(serializers.Serializer):
    """
    Serializer for returning an employee's complete permissions profile.
    Used by the frontend RoleContext.
    """
    
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    primary_role = serializers.DictField(allow_null=True)
    all_roles = serializers.ListField()
    effective_permissions = serializers.ListField()
    highest_level = serializers.IntegerField()
    approval_scope = serializers.CharField()
    is_hr = serializers.BooleanField()
    can_approve = serializers.BooleanField()


class BulkRoleAssignmentSerializer(serializers.Serializer):
    """Serializer for bulk role assignment operations"""
    
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    role_id = serializers.IntegerField()
    department_scope = serializers.IntegerField(required=False, allow_null=True)
    program_scope = serializers.IntegerField(required=False, allow_null=True)
    is_primary = serializers.BooleanField(default=False)
    valid_from = serializers.DateTimeField(required=False, allow_null=True)
    valid_until = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
