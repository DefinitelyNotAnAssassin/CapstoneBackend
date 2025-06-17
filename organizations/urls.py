from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, DepartmentViewSet, ProgramViewSet,
    OfficeViewSet, PositionViewSet
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'offices', OfficeViewSet)
router.register(r'positions', PositionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
