from rest_framework import viewsets
from .models import LeavePolicy
from .serializers import LeavePolicySerializer
from leave_requests.utils import get_authenticated_employee


class LeavePolicyViewSet(viewsets.ModelViewSet):
    queryset = LeavePolicy.objects.all()
    serializer_class = LeavePolicySerializer

    def create(self, request, *args, **kwargs):
        authenticated_employee = get_authenticated_employee(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        authenticated_employee = get_authenticated_employee(request)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        authenticated_employee = get_authenticated_employee(request)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        authenticated_employee = get_authenticated_employee(request)
        return super().destroy(request, *args, **kwargs)
