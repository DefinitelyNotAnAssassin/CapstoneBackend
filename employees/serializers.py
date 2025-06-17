from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Employee, EmployeeEducation, EmployeeSibling, EmployeeDependent,
    EmployeeAward, EmployeeLicense, EmployeeSchedule
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class EmployeeEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeEducation
        fields = '__all__'


class EmployeeSiblingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSibling
        fields = '__all__'


class EmployeeDependentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDependent
        fields = '__all__'


class EmployeeAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAward
        fields = '__all__'


class EmployeeLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLicense
        fields = '__all__'


class EmployeeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSchedule
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    # Related fields (read-only)
    position_title = serializers.CharField(source='position.title', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    office_name = serializers.CharField(source='office.name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    # Nested serializers for related data
    additional_education = EmployeeEducationSerializer(many=True, read_only=True)
    siblings = EmployeeSiblingSerializer(many=True, read_only=True)
    dependents = EmployeeDependentSerializer(many=True, read_only=True)
    awards = EmployeeAwardSerializer(many=True, read_only=True)
    licenses = EmployeeLicenseSerializer(many=True, read_only=True)
    schedules = EmployeeScheduleSerializer(many=True, read_only=True)
    
    # User creation fields (write-only)
    password = serializers.CharField(write_only=True, required=False, default='sdca2025')
    username = serializers.CharField(write_only=True, required=False)
    
    # Date fields with flexible input formats
    birth_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'], required=False)
    date_hired = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'], required=False)
    
    class Meta:
        model = Employee
        fields = '__all__'
        
    def create(self, validated_data):
        # Extract user creation data
        password = validated_data.pop('password', 'sdca2025')
        username = validated_data.pop('username', None)
        
        # Create user if email is provided
        user = None
        if validated_data.get('email'):
            user_data = {
                'username': username or validated_data['email'],
                'email': validated_data['email'],
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
            }
            user = User.objects.create_user(password=password, **user_data)
            validated_data['user'] = user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Remove user-related fields from update
        validated_data.pop('password', None)
        validated_data.pop('username', None)
        
        # Update user fields if user exists
        if instance.user:
            instance.user.email = validated_data.get('email', instance.user.email)
            instance.user.first_name = validated_data.get('first_name', instance.user.first_name)
            instance.user.last_name = validated_data.get('last_name', instance.user.last_name)
            instance.user.save()
        
        return super().update(instance, validated_data)


class EmployeeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    position_title = serializers.CharField(source='position.title', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    office_name = serializers.CharField(source='office.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'middle_name', 'last_name', 
            'full_name', 'email', 'mobile_no', 'position_title', 
            'department_name', 'office_name', 'profile_image', 'is_active'
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating employees with user account"""
    password = serializers.CharField(write_only=True, min_length=6, required=False, default='sdca2025')
    username = serializers.CharField(write_only=True, required=False)
    
    # Education data
    additional_education = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )
    
    # Date fields with proper formatting
    birth_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'])
    date_hired = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'])
    
    class Meta:
        model = Employee
        fields = '__all__'
        
    def validate_password(self, value):
        """Provide default password if not supplied"""
        if not value:
            return 'sdca2025'
        return value
        
    def create(self, validated_data):
        # Extract additional education data
        additional_education_data = validated_data.pop('additional_education', [])
        
        # Extract user creation data
        password = validated_data.pop('password', 'sdca2025')
        username = validated_data.pop('username', validated_data['email'])
        
        # Create user account
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        validated_data['user'] = user
        
        # Create employee
        employee = super().create(validated_data)
        
        # Create additional education records
        for edu_data in additional_education_data:
            EmployeeEducation.objects.create(
                employee=employee,
                level=edu_data.get('degree', ''),
                school=edu_data.get('school', ''),
                course=edu_data.get('course', ''),
                year_started=edu_data.get('year', ''),
                year_ended=edu_data.get('year', ''),
                graduated=True
            )
        
        return employee
