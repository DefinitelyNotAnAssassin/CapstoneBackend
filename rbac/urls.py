"""
RBAC URL Configuration

URL patterns for Role-Based Access Control API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'employee-roles', views.EmployeeRoleViewSet, basename='employee-role')
router.register(r'modules', views.PermissionModuleViewSet, basename='permission-module')
router.register(r'change-logs', views.RBACChangeLogViewSet, basename='rbac-change-log')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Custom endpoints
    path('employee/<int:employee_id>/permissions/', views.get_employee_permissions, name='employee-permissions'),
    path('employee/permissions/by-email/', views.get_employee_permissions_by_email, name='employee-permissions-by-email'),
    path('check-permission/', views.check_permission, name='check-permission'),
    path('stats/', views.rbac_stats, name='rbac-stats'),
]
