from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeavePolicyViewSet

router = DefaultRouter()
router.register(r'leave-policies', LeavePolicyViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
