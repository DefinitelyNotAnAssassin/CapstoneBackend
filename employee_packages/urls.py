from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeavePackageViewSet

router = DefaultRouter()
router.register(r'employee-packages', LeavePackageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
