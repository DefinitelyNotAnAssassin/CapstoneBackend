from rest_framework import serializers
from .models import LeavePolicy, LeaveRequest, LeaveCredit, LeaveBalance


class LeavePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePolicy
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
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


class LeaveCreditSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = LeaveCredit
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = '__all__'
