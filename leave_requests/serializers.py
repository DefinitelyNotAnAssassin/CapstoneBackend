from datetime import date

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
        """Validate leave request with business rules"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        days_requested = data.get('days_requested')
        leave_type = data.get('leave_type')
        employee = data.get('employee')
        today = date.today()
        
        # Validate business days calculation
        if start_date and end_date and days_requested is not None:
            calculated_days = calculate_business_days(start_date, end_date)
            if days_requested != calculated_days:
                raise serializers.ValidationError({
                    'days_requested': f'Days requested ({days_requested}) does not match calculated business days ({calculated_days}). Business days are calculated Monday to Saturday, excluding Sunday.'
                })
        
        # --- Gender-based leave validation ---
        if employee and leave_type:
            gender = getattr(employee, 'gender', None)
            if leave_type == 'Maternity Leave' and gender != 'Female':
                raise serializers.ValidationError({
                    'leave_type': 'Maternity Leave is only available for female employees.'
                })
            if leave_type == 'Paternity Leave' and gender != 'Male':
                raise serializers.ValidationError({
                    'leave_type': 'Paternity Leave is only available for male employees.'
                })
        
        # --- Sick leave: only past or current dates ---
        if leave_type == 'Sick Leave':
            if start_date and start_date > today:
                raise serializers.ValidationError({
                    'start_date': 'Sick Leave can only be applied for past or current dates, not in advance.'
                })
            if end_date and end_date > today:
                raise serializers.ValidationError({
                    'end_date': 'Sick Leave end date cannot be a future date.'
                })
        
        # --- Birthday leave: only during birthday month ---
        if leave_type == 'Birthday Leave' and employee:
            birth_date = getattr(employee, 'birth_date', None)
            if birth_date:
                if start_date and start_date.month != birth_date.month:
                    raise serializers.ValidationError({
                        'start_date': f'Birthday Leave can only be taken during your birthday month ({birth_date.strftime("%B")}).'
                    })
                if end_date and end_date.month != birth_date.month:
                    raise serializers.ValidationError({
                        'end_date': f'Birthday Leave must end within your birthday month ({birth_date.strftime("%B")}).'
                    })
            else:
                raise serializers.ValidationError({
                    'leave_type': 'Birthday Leave requires a birth date on file. Please contact HR.'
                })
        
        return data
