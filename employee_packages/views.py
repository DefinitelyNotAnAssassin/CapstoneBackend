from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from .models import LeavePackage, LeavePackageItem
from .serializers import LeavePackageSerializer, LeavePackageCreateSerializer
from leave_credits.models import LeaveCredit


class LeavePackageViewSet(viewsets.ModelViewSet):
    queryset = LeavePackage.objects.prefetch_related('items').all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return LeavePackageCreateSerializer
        return LeavePackageSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Optionally filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_predefined:
            return Response(
                {"error": "Predefined packages cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='apply-to-employee')
    def apply_to_employee(self, request, pk=None):
        """
        Apply this leave package to a specific employee.
        Creates leave credits for the current year based on the package items.
        
        Expects: { "employee_id": <int> }
        """
        package = self.get_object()
        employee_id = request.data.get('employee_id')

        if not employee_id:
            return Response(
                {"error": "employee_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from employees.models import Employee
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        year = datetime.now().year
        created_credits = []

        for item in package.items.all():
            credit, created = LeaveCredit.objects.update_or_create(
                employee=employee,
                leave_type=item.leave_type,
                year=year,
                defaults={
                    'total_credits': item.quantity,
                    'remaining_credits': item.quantity,
                    'used_credits': 0,
                },
            )
            created_credits.append({
                'leave_type': item.leave_type,
                'quantity': str(item.quantity),
                'created': created,
            })

        return Response({
            "message": f"Leave package '{package.name}' applied to {employee.full_name}.",
            "credits": created_credits,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='leave-types')
    def leave_types(self, request):
        """Return available leave types for building custom packages."""
        from leave_requests.models import LeaveRequest
        types = [{'value': lt[0], 'label': lt[1]} for lt in LeaveRequest.LEAVE_TYPES]
        return Response(types)
