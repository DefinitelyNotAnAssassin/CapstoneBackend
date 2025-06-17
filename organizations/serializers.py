from rest_framework import serializers
from .models import Organization, Department, Program, Office, Position


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    head_name = serializers.CharField(source='head.full_name', read_only=True)
    
    class Meta:
        model = Department
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    chair_name = serializers.CharField(source='chair.full_name', read_only=True)
    
    class Meta:
        model = Program
        fields = '__all__'


class OfficeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Office
        fields = '__all__'
