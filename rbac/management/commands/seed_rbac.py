"""
Management command to seed initial RBAC permissions and roles.

This command creates the default permissions, roles, and role-permission
mappings needed for the leave management system.

Usage:
    python manage.py seed_rbac
    python manage.py seed_rbac --reset  # Clear and reseed
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from rbac.models import Permission, Role, RolePermission, PermissionModule


class Command(BaseCommand):
    help = 'Seed initial RBAC permissions and roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Clear existing RBAC data before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Clearing existing RBAC data...')
            RolePermission.objects.all().delete()
            Role.objects.all().delete()
            Permission.objects.all().delete()
            PermissionModule.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        with transaction.atomic():
            self.create_permissions()
            self.create_roles()
            self.create_modules()
            self.assign_role_permissions()

        self.stdout.write(self.style.SUCCESS('RBAC seeding completed successfully!'))

    def create_permissions(self):
        """Create all system permissions"""
        self.stdout.write('Creating permissions...')
        
        permissions_data = [
            # Leave Management Permissions
            {'code': 'leave_view_own', 'name': 'View Own Leave Requests', 'category': 'leave',
             'description': 'Can view their own leave requests and balances', 'is_system': True},
            {'code': 'leave_create', 'name': 'Create Leave Requests', 'category': 'leave',
             'description': 'Can submit new leave requests', 'is_system': True},
            {'code': 'leave_cancel_own', 'name': 'Cancel Own Leave Requests', 'category': 'leave',
             'description': 'Can cancel their own pending leave requests', 'is_system': True},
            {'code': 'leave_view_team', 'name': 'View Team Leave Requests', 'category': 'leave',
             'description': 'Can view leave requests of team members', 'is_system': True},
            {'code': 'leave_view_department', 'name': 'View Department Leave Requests', 'category': 'leave',
             'description': 'Can view all leave requests in their department', 'is_system': True},
            {'code': 'leave_view_all', 'name': 'View All Leave Requests', 'category': 'leave',
             'description': 'Can view all leave requests across the organization', 'is_system': True},
            {'code': 'leave_approve_program', 'name': 'Approve Leave (Program)', 'category': 'leave',
             'description': 'Can pre-approve leave requests within their program', 'is_system': True},
            {'code': 'leave_approve_department', 'name': 'Approve Leave (Department)', 'category': 'leave',
             'description': 'Can pre-approve leave requests within their department', 'is_system': True},
            {'code': 'leave_approve_all', 'name': 'Approve Leave (Organization)', 'category': 'leave',
             'description': 'Can pre-approve any leave request in the organization', 'is_system': True},
            {'code': 'leave_final_approval', 'name': 'Final Leave Approval (HR)', 'category': 'leave',
             'description': 'Can give final HR approval on pre-approved leave requests', 'is_system': True},
            {'code': 'leave_reject', 'name': 'Reject Leave Requests', 'category': 'leave',
             'description': 'Can reject leave requests', 'is_system': True},
            {'code': 'leave_manage_credits', 'name': 'Manage Leave Credits', 'category': 'leave',
             'description': 'Can adjust leave credit balances for employees', 'is_system': True},
            {'code': 'leave_manage_policies', 'name': 'Manage Leave Policies', 'category': 'leave',
             'description': 'Can create and modify leave policies', 'is_system': True},
            {'code': 'leave_force_approve', 'name': 'Force Approve Leave', 'category': 'leave',
             'description': 'Can approve leave requests even without sufficient credits', 'is_system': True},
            
            # Employee Management Permissions
            {'code': 'employee_view_own', 'name': 'View Own Profile', 'category': 'employee',
             'description': 'Can view their own employee profile', 'is_system': True},
            {'code': 'employee_edit_own', 'name': 'Edit Own Profile', 'category': 'employee',
             'description': 'Can edit certain fields of their own profile', 'is_system': True},
            {'code': 'employee_view_team', 'name': 'View Team Profiles', 'category': 'employee',
             'description': 'Can view profiles of team members', 'is_system': True},
            {'code': 'employee_view_department', 'name': 'View Department Profiles', 'category': 'employee',
             'description': 'Can view all employee profiles in their department', 'is_system': True},
            {'code': 'employee_view_all', 'name': 'View All Employees', 'category': 'employee',
             'description': 'Can view all employee profiles', 'is_system': True},
            {'code': 'employee_create', 'name': 'Create Employees', 'category': 'employee',
             'description': 'Can create new employee records', 'is_system': True},
            {'code': 'employee_edit_all', 'name': 'Edit All Employees', 'category': 'employee',
             'description': 'Can edit any employee profile', 'is_system': True},
            {'code': 'employee_delete', 'name': 'Delete Employees', 'category': 'employee',
             'description': 'Can delete employee records', 'is_system': True},
            {'code': 'employee_manage_schedule', 'name': 'Manage Schedules', 'category': 'employee',
             'description': 'Can manage employee work schedules', 'is_system': True},
            
            # Reports & Analytics Permissions
            {'code': 'reports_view_team', 'name': 'View Team Reports', 'category': 'reports',
             'description': 'Can view reports for their team', 'is_system': True},
            {'code': 'reports_view_department', 'name': 'View Department Reports', 'category': 'reports',
             'description': 'Can view department-level reports', 'is_system': True},
            {'code': 'reports_view_all', 'name': 'View All Reports', 'category': 'reports',
             'description': 'Can view all organizational reports', 'is_system': True},
            {'code': 'reports_export', 'name': 'Export Reports', 'category': 'reports',
             'description': 'Can export reports to various formats', 'is_system': True},
            {'code': 'reports_analytics', 'name': 'View Analytics Dashboard', 'category': 'reports',
             'description': 'Can access the analytics dashboard', 'is_system': True},
            
            # Organization Management Permissions
            {'code': 'org_view', 'name': 'View Organization Structure', 'category': 'organization',
             'description': 'Can view organizational structure', 'is_system': True},
            {'code': 'org_manage_departments', 'name': 'Manage Departments', 'category': 'organization',
             'description': 'Can create and modify departments', 'is_system': True},
            {'code': 'org_manage_programs', 'name': 'Manage Programs', 'category': 'organization',
             'description': 'Can create and modify programs', 'is_system': True},
            {'code': 'org_manage_positions', 'name': 'Manage Positions', 'category': 'organization',
             'description': 'Can create and modify positions', 'is_system': True},
            
            # System Settings Permissions
            {'code': 'settings_view', 'name': 'View System Settings', 'category': 'settings',
             'description': 'Can view system configuration', 'is_system': True},
            {'code': 'settings_edit', 'name': 'Edit System Settings', 'category': 'settings',
             'description': 'Can modify system configuration', 'is_system': True},
            {'code': 'rbac_view', 'name': 'View RBAC Settings', 'category': 'settings',
             'description': 'Can view roles and permissions', 'is_system': True},
            {'code': 'rbac_manage_roles', 'name': 'Manage Roles', 'category': 'settings',
             'description': 'Can create, edit, and delete roles', 'is_system': True},
            {'code': 'rbac_manage_permissions', 'name': 'Manage Permissions', 'category': 'settings',
             'description': 'Can create custom permissions', 'is_system': True},
            {'code': 'rbac_assign_roles', 'name': 'Assign Roles to Employees', 'category': 'settings',
             'description': 'Can assign roles to employees', 'is_system': True},
            
            # Audit & Compliance Permissions
            {'code': 'audit_view', 'name': 'View Audit Logs', 'category': 'audit',
             'description': 'Can view system audit logs', 'is_system': True},
            {'code': 'audit_export', 'name': 'Export Audit Logs', 'category': 'audit',
             'description': 'Can export audit logs', 'is_system': True},
            
            # Special Permissions
            {'code': 'hr_full_access', 'name': 'HR Full Access', 'category': 'settings',
             'description': 'Complete administrative access - HR only', 'is_system': True},
        ]
        
        created_count = 0
        for perm_data in permissions_data:
            perm, created = Permission.objects.get_or_create(
                code=perm_data['code'],
                defaults=perm_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  Created {created_count} new permissions')

    def create_roles(self):
        """Create default system roles"""
        self.stdout.write('Creating roles...')
        
        roles_data = [
            {
                'name': 'HR Administrator',
                'code': 'HR_ADMIN',
                'description': 'Full administrative access to all HR functions including final leave approval',
                'level': -1,
                'approval_scope': 'all',
                'is_system': True,
            },
            {
                'name': 'Vice President for Academic Affairs',
                'code': 'VPAA',
                'description': 'Top academic authority with organization-wide approval rights',
                'level': 0,
                'approval_scope': 'all',
                'is_system': True,
            },
            {
                'name': 'Dean',
                'code': 'DEAN',
                'description': 'Department head with department-level approval rights',
                'level': 1,
                'approval_scope': 'department',
                'is_system': True,
            },
            {
                'name': 'Program Chair',
                'code': 'PROGRAM_CHAIR',
                'description': 'Program head with program-level approval rights',
                'level': 2,
                'approval_scope': 'program',
                'is_system': True,
            },
            {
                'name': 'Regular Faculty',
                'code': 'REGULAR_FACULTY',
                'description': 'Full-time faculty member',
                'level': 3,
                'approval_scope': 'none',
                'is_system': True,
            },
            {
                'name': 'Part-Time Faculty',
                'code': 'PART_TIME_FACULTY',
                'description': 'Part-time faculty member',
                'level': 4,
                'approval_scope': 'none',
                'is_system': True,
            },
            {
                'name': 'Secretary',
                'code': 'SECRETARY',
                'description': 'Administrative support staff',
                'level': 5,
                'approval_scope': 'none',
                'is_system': True,
            },
            {
                'name': 'Basic Employee',
                'code': 'EMPLOYEE',
                'description': 'Standard employee with basic access',
                'level': 5,
                'approval_scope': 'none',
                'is_system': True,
            },
        ]
        
        created_count = 0
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                code=role_data['code'],
                defaults=role_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  Created {created_count} new roles')

    def create_modules(self):
        """Create permission modules for UI organization"""
        self.stdout.write('Creating permission modules...')
        
        modules_data = [
            {
                'name': 'Leave Management',
                'code': 'LEAVE',
                'description': 'Leave request and approval management',
                'icon': 'calendar',
                'order': 1,
                'permission_codes': [
                    'leave_view_own', 'leave_create', 'leave_cancel_own', 'leave_view_team',
                    'leave_view_department', 'leave_view_all', 'leave_approve_program',
                    'leave_approve_department', 'leave_approve_all', 'leave_final_approval',
                    'leave_reject', 'leave_manage_credits', 'leave_manage_policies', 'leave_force_approve'
                ]
            },
            {
                'name': 'Employee Management',
                'code': 'EMPLOYEE',
                'description': 'Employee profiles and records management',
                'icon': 'people',
                'order': 2,
                'permission_codes': [
                    'employee_view_own', 'employee_edit_own', 'employee_view_team',
                    'employee_view_department', 'employee_view_all', 'employee_create',
                    'employee_edit_all', 'employee_delete', 'employee_manage_schedule'
                ]
            },
            {
                'name': 'Reports & Analytics',
                'code': 'REPORTS',
                'description': 'Reporting and analytics access',
                'icon': 'analytics',
                'order': 3,
                'permission_codes': [
                    'reports_view_team', 'reports_view_department', 'reports_view_all',
                    'reports_export', 'reports_analytics'
                ]
            },
            {
                'name': 'Organization',
                'code': 'ORGANIZATION',
                'description': 'Organization structure management',
                'icon': 'business',
                'order': 4,
                'permission_codes': [
                    'org_view', 'org_manage_departments', 'org_manage_programs', 'org_manage_positions'
                ]
            },
            {
                'name': 'Access Control',
                'code': 'RBAC',
                'description': 'Role and permission management',
                'icon': 'key',
                'order': 5,
                'permission_codes': [
                    'rbac_view', 'rbac_manage_roles', 'rbac_manage_permissions', 'rbac_assign_roles'
                ]
            },
            {
                'name': 'System Settings',
                'code': 'SETTINGS',
                'description': 'System configuration and settings',
                'icon': 'settings',
                'order': 6,
                'permission_codes': ['settings_view', 'settings_edit', 'hr_full_access']
            },
            {
                'name': 'Audit & Compliance',
                'code': 'AUDIT',
                'description': 'Audit logs and compliance tracking',
                'icon': 'shield',
                'order': 7,
                'permission_codes': ['audit_view', 'audit_export']
            },
        ]
        
        created_count = 0
        for module_data in modules_data:
            permission_codes = module_data.pop('permission_codes', [])
            module, created = PermissionModule.objects.get_or_create(
                code=module_data['code'],
                defaults=module_data
            )
            
            if created:
                created_count += 1
            
            # Add permissions to module
            permissions = Permission.objects.filter(code__in=permission_codes)
            module.permissions.set(permissions)
        
        self.stdout.write(f'  Created {created_count} new permission modules')

    def assign_role_permissions(self):
        """Assign permissions to roles"""
        self.stdout.write('Assigning permissions to roles...')
        
        role_permissions = {
            'HR_ADMIN': [
                # All permissions
                'leave_view_own', 'leave_create', 'leave_cancel_own', 'leave_view_team',
                'leave_view_department', 'leave_view_all', 'leave_approve_program',
                'leave_approve_department', 'leave_approve_all', 'leave_final_approval',
                'leave_reject', 'leave_manage_credits', 'leave_manage_policies', 'leave_force_approve',
                'employee_view_own', 'employee_edit_own', 'employee_view_team',
                'employee_view_department', 'employee_view_all', 'employee_create',
                'employee_edit_all', 'employee_delete', 'employee_manage_schedule',
                'reports_view_team', 'reports_view_department', 'reports_view_all',
                'reports_export', 'reports_analytics',
                'org_view', 'org_manage_departments', 'org_manage_programs', 'org_manage_positions',
                'settings_view', 'settings_edit', 'rbac_view', 'rbac_manage_roles',
                'rbac_manage_permissions', 'rbac_assign_roles',
                'audit_view', 'audit_export', 'hr_full_access'
            ],
            'VPAA': [
                'leave_view_own', 'leave_create', 'leave_cancel_own', 'leave_view_all',
                'leave_approve_all', 'leave_reject', 'leave_manage_credits', 'leave_manage_policies',
                'employee_view_own', 'employee_edit_own', 'employee_view_all', 'employee_create',
                'employee_edit_all', 'employee_manage_schedule',
                'reports_view_all', 'reports_export', 'reports_analytics',
                'org_view', 'org_manage_departments', 'org_manage_programs', 'org_manage_positions',
                'settings_view', 'rbac_view', 'audit_view'
            ],
            'DEAN': [
                'leave_view_own', 'leave_create', 'leave_cancel_own', 'leave_view_department',
                'leave_approve_department', 'leave_reject', 'leave_manage_credits',
                'employee_view_own', 'employee_edit_own', 'employee_view_department',
                'reports_view_department', 'reports_export',
                'org_view', 'rbac_view'
            ],
            'PROGRAM_CHAIR': [
                'leave_view_own', 'leave_create', 'leave_cancel_own', 'leave_view_team',
                'leave_approve_program', 'leave_reject',
                'employee_view_own', 'employee_edit_own', 'employee_view_team',
                'reports_view_team',
                'org_view'
            ],
            'REGULAR_FACULTY': [
                'leave_view_own', 'leave_create', 'leave_cancel_own',
                'employee_view_own', 'employee_edit_own',
                'org_view'
            ],
            'PART_TIME_FACULTY': [
                'leave_view_own', 'leave_create', 'leave_cancel_own',
                'employee_view_own', 'employee_edit_own',
                'org_view'
            ],
            'SECRETARY': [
                'leave_view_own', 'leave_create', 'leave_cancel_own',
                'employee_view_own', 'employee_edit_own',
                'org_view'
            ],
            'EMPLOYEE': [
                'leave_view_own', 'leave_create', 'leave_cancel_own',
                'employee_view_own', 'employee_edit_own',
                'org_view'
            ],
        }
        
        assignment_count = 0
        for role_code, permission_codes in role_permissions.items():
            try:
                role = Role.objects.get(code=role_code)
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Role {role_code} not found, skipping'))
                continue
            
            for perm_code in permission_codes:
                try:
                    permission = Permission.objects.get(code=perm_code)
                    rp, created = RolePermission.objects.get_or_create(
                        role=role,
                        permission=permission
                    )
                    if created:
                        assignment_count += 1
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'  Permission {perm_code} not found'))
        
        self.stdout.write(f'  Created {assignment_count} new role-permission assignments')
