from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeavePolicyViewSet, LeaveRequestViewSet, LeaveCreditViewSet
)

router = DefaultRouter()
router.register(r'leave-policies', LeavePolicyViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'leave-credits', LeaveCreditViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
