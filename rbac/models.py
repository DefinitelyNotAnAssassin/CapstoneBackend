"""
RBAC (Role-Based Access Control) Models

This module provides a flexible, customizable permission system that allows HR
to configure roles and permissions dynamically without code changes.

Architecture:
- Permission: Individual capabilities (e.g., 'can_approve_leave', 'can_view_reports')
- Role: Collection of permissions assigned to users
- UserRole: Links employees to roles with optional scope limitations
"""

from django.db import models
from django.core.validators import RegexValidator


class Permission(models.Model):
    """
    Represents an individual permission/capability in the system.
    Permissions are atomic actions that can be granted to roles.
    """
    
    # Permission categories for organization
    CATEGORY_CHOICES = [
        ('leave', 'Leave Management'),
        ('employee', 'Employee Management'),
        ('reports', 'Reports & Analytics'),
        ('settings', 'System Settings'),
        ('organization', 'Organization Management'),
        ('audit', 'Audit & Compliance'),
    ]
    
    code = models.CharField(
        max_length=100, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-z][a-z0-9_]*$',
            message='Permission code must be lowercase alphanumeric with underscores, starting with a letter'
        )],
        help_text="Unique identifier for the permission (e.g., 'can_approve_leave')"
    )
    name = models.CharField(
        max_length=255,
        help_text="Human-readable name for the permission"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this permission allows"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='settings',
        help_text="Category for grouping permissions in the UI"
    )
    is_system = models.BooleanField(
        default=False,
        help_text="System permissions cannot be deleted by HR"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive permissions are not enforced"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Role(models.Model):
    """
    Represents a role that groups multiple permissions together.
    Roles can be assigned to employees to grant them capabilities.
    """
    
    # Predefined role levels for approval hierarchy
    LEVEL_CHOICES = [
        (-1, 'Super Admin (HR)'),
        (0, 'Executive (VPAA)'),
        (1, 'Department Head (Dean)'),
        (2, 'Program Head (Chair)'),
        (3, 'Senior Staff'),
        (4, 'Staff'),
        (5, 'Basic User'),
        (99, 'Guest/Limited'),
    ]
    
    # Approval scope options
    SCOPE_CHOICES = [
        ('none', 'No Approval Rights'),
        ('program', 'Program Level'),
        ('department', 'Department Level'),
        ('organization', 'Organization Level'),
        ('all', 'Global Access'),
    ]
    
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique name for the role"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z][A-Z0-9_]*$',
            message='Role code must be uppercase alphanumeric with underscores, starting with a letter'
        )],
        help_text="Unique code identifier (e.g., 'HR_ADMIN', 'DEAN')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this role's responsibilities"
    )
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        default=5,
        help_text="Hierarchical level for approval chain (lower = higher authority)"
    )
    approval_scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default='none',
        help_text="What scope of items can this role approve"
    )
    
    # Role settings
    is_system = models.BooleanField(
        default=False,
        help_text="System roles cannot be deleted by HR"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive roles are not enforced"
    )
    can_be_assigned = models.BooleanField(
        default=True,
        help_text="Whether this role can be assigned to new employees"
    )
    
    # Permissions linked to this role
    permissions = models.ManyToManyField(
        Permission,
        through='RolePermission',
        related_name='roles',
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_roles'
    )
    
    class Meta:
        ordering = ['level', 'name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"
    
    def get_all_permissions(self):
        """Get all active permission codes for this role"""
        return list(
            self.role_permissions.filter(
                is_active=True,
                permission__is_active=True
            ).values_list('permission__code', flat=True)
        )
    
    def has_permission(self, permission_code):
        """Check if this role has a specific permission"""
        return self.role_permissions.filter(
            permission__code=permission_code,
            permission__is_active=True,
            is_active=True
        ).exists()


class RolePermission(models.Model):
    """
    Through model linking roles to permissions with additional metadata.
    Allows for conditional permission grants (e.g., time-limited, with conditions).
    """
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='permission_roles'
    )
    
    # Optional conditions
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this permission grant is currently active"
    )
    conditions = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional JSON conditions for this permission (e.g., {'max_amount': 10000})"
    )
    
    # Metadata
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_permissions'
    )
    
    class Meta:
        unique_together = ['role', 'permission']
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
    
    def __str__(self):
        return f"{self.role.name} -> {self.permission.code}"


class EmployeeRole(models.Model):
    """
    Links employees to roles with optional scope limitations.
    An employee can have multiple roles with different scopes.
    """
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='employee_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='employee_assignments'
    )
    
    # Scope limitations (optional - if null, uses role's default scope)
    department_scope = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scoped_roles',
        help_text="Limit this role to a specific department"
    )
    program_scope = models.ForeignKey(
        'organizations.Program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scoped_roles',
        help_text="Limit this role to a specific program"
    )
    
    # Role assignment settings
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary role determines the employee's main dashboard view"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role assignment is currently active"
    )
    
    # Time-limited assignments
    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this role assignment becomes active (null = immediately)"
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this role assignment expires (null = never)"
    )
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_assignments_made'
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes about this role assignment"
    )
    
    class Meta:
        ordering = ['-is_primary', 'role__level']
        verbose_name = 'Employee Role'
        verbose_name_plural = 'Employee Roles'
        # An employee can only have each role once per scope
        unique_together = ['employee', 'role', 'department_scope', 'program_scope']
    
    def __str__(self):
        scope = ""
        if self.department_scope:
            scope = f" (Dept: {self.department_scope.name})"
        elif self.program_scope:
            scope = f" (Prog: {self.program_scope.name})"
        return f"{self.employee.full_name} -> {self.role.name}{scope}"
    
    def is_valid(self):
        """Check if this role assignment is currently valid (active and within time bounds)"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        return True


class PermissionModule(models.Model):
    """
    Represents a system module for organizing permissions in the UI.
    Used primarily for the HR permission management interface.
    """
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name for UI display")
    order = models.IntegerField(default=0, help_text="Display order in the UI")
    is_active = models.BooleanField(default=True)
    
    # Permissions in this module
    permissions = models.ManyToManyField(
        Permission,
        related_name='modules',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Permission Module'
        verbose_name_plural = 'Permission Modules'
    
    def __str__(self):
        return self.name


class RBACChangeLog(models.Model):
    """
    Tracks all RBAC-related changes for compliance and debugging.
    """
    
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('assign', 'Role Assigned'),
        ('revoke', 'Role Revoked'),
        ('grant', 'Permission Granted'),
        ('deny', 'Permission Denied'),
    ]
    
    MODEL_CHOICES = [
        ('permission', 'Permission'),
        ('role', 'Role'),
        ('role_permission', 'Role Permission'),
        ('employee_role', 'Employee Role'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES)
    model_id = models.IntegerField()
    
    # Change details
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    
    # Who made the change
    performed_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='rbac_audit_logs'
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Optional reference to affected employee (for role assignments)
    affected_employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rbac_changes_received'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-performed_at']
        verbose_name = 'RBAC Change Log'
        verbose_name_plural = 'RBAC Change Logs'
    
    def __str__(self):
        return f"{self.get_action_display()} {self.model_type} #{self.model_id} by {self.performed_by}"
