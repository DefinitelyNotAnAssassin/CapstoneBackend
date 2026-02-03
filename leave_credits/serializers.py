from rest_framework import serializers
from .models import LeaveCredit, LeaveBalance


class LeaveCreditSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    remaining_credits = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, read_only=True)
    
    class Meta:
        model = LeaveCredit
        fields = '__all__'
    
    def create(self, validated_data):
        # Remove remaining_credits if provided, let the model calculate it
        validated_data.pop('remaining_credits', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Remove remaining_credits if provided, let the model calculate it
        validated_data.pop('remaining_credits', None)
        return super().update(instance, validated_data)


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = '__all__'
