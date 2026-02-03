from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Permission, Role, RolePermission, EmployeeRole, PermissionModule, RBACChangeLog


@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = ['code', 'name', 'category', 'is_system', 'is_active']
    list_filter = ['category', 'is_system', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['category', 'name']


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    raw_id_fields = ['permission']


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ['name', 'code', 'level', 'approval_scope', 'is_system', 'is_active']
    list_filter = ['level', 'approval_scope', 'is_system', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['level', 'name']
    inlines = [RolePermissionInline]


@admin.register(RolePermission)
class RolePermissionAdmin(ModelAdmin):
    list_display = ['role', 'permission', 'is_active', 'granted_at']
    list_filter = ['is_active', 'role']
    search_fields = ['role__name', 'permission__code', 'permission__name']
    raw_id_fields = ['role', 'permission']


@admin.register(EmployeeRole)
class EmployeeRoleAdmin(ModelAdmin):
    list_display = ['employee', 'role', 'is_primary', 'is_active', 'assigned_at']
    list_filter = ['is_primary', 'is_active', 'role']
    search_fields = ['employee__first_name', 'employee__last_name', 'role__name']
    raw_id_fields = ['employee', 'role', 'department_scope', 'program_scope']


@admin.register(PermissionModule)
class PermissionModuleAdmin(ModelAdmin):
    list_display = ['name', 'code', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    filter_horizontal = ['permissions']


@admin.register(RBACChangeLog)
class RBACChangeLogAdmin(ModelAdmin):
    list_display = ['action', 'model_type', 'model_id', 'performed_by', 'performed_at']
    list_filter = ['action', 'model_type', 'performed_at']
    search_fields = ['notes']
    readonly_fields = ['action', 'model_type', 'model_id', 'previous_value', 'new_value', 
                       'performed_by', 'performed_at', 'ip_address', 'user_agent', 
                       'affected_employee', 'notes']
