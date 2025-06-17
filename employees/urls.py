from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, EmployeeEducationViewSet, EmployeeSiblingViewSet,
    EmployeeDependentViewSet, EmployeeAwardViewSet, EmployeeLicenseViewSet,
    EmployeeScheduleViewSet, login_view, verify_token, logout_view, demo_login
)

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'employee-education', EmployeeEducationViewSet)
router.register(r'employee-siblings', EmployeeSiblingViewSet)
router.register(r'employee-dependents', EmployeeDependentViewSet)
router.register(r'employee-awards', EmployeeAwardViewSet)
router.register(r'employee-licenses', EmployeeLicenseViewSet)
router.register(r'employee-schedules', EmployeeScheduleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    
    # Authentication endpoints
    path('api/auth/login/', login_view, name='employee-login'),
    path('api/auth/verify-token/', verify_token, name='verify-token'),
    path('api/auth/logout/', logout_view, name='employee-logout'),
    path('api/auth/demo-login/', demo_login, name='demo-login'),
]
