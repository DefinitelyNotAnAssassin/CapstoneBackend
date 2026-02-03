from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaveCreditViewSet, LeaveBalanceViewSet

router = DefaultRouter()
router.register(r'leave-credits', LeaveCreditViewSet)
router.register(r'leave-balances', LeaveBalanceViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
