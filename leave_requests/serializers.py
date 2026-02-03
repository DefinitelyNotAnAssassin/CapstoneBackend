from rest_framework import serializers
from .models import LeaveRequest
from .utils import calculate_business_days
from employees.serializers import EmployeeListSerializer
from employees.models import Employee


class ApprovedByMiniSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    position = serializers.CharField(source='position.title', default="")

    class Meta:
        model = Employee
        fields = ['id', 'first_name', 'last_name', 'position']


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    supervisor_approved_by_name = serializers.CharField(source='supervisor_approved_by.full_name', read_only=True)
    approved_by = ApprovedByMiniSerializer(read_only=True)
    supervisor_approved_by = ApprovedByMiniSerializer(read_only=True)
    employee = EmployeeListSerializer(read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = [
            'employee', 'leave_type', 'start_date', 'end_date', 
            'days_requested', 'reason', 'supporting_documents'
        ]
    
    def validate(self, data):
        """Validate that days_requested matches the calculated business days"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        days_requested = data.get('days_requested')
        
        if start_date and end_date and days_requested is not None:
            calculated_days = calculate_business_days(start_date, end_date)
            if days_requested != calculated_days:
                raise serializers.ValidationError({
                    'days_requested': f'Days requested ({days_requested}) does not match calculated business days ({calculated_days}). Business days are calculated Monday to Saturday, excluding Sunday.'
                })
        
        return data
