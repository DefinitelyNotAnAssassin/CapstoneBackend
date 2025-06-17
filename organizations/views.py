from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Organization, Department, Program, Office, Position
from .serializers import (
    OrganizationSerializer, DepartmentSerializer, ProgramSerializer,
    OfficeSerializer, PositionSerializer
)


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('organization', 'head').all()
    serializer_class = DepartmentSerializer
    
    @action(detail=False, methods=['get'])
    def by_organization(self, request):
        """Get departments by organization ID"""
        org_id = request.query_params.get('organization_id')
        if org_id:
            departments = self.queryset.filter(organization_id=org_id)
            serializer = self.get_serializer(departments, many=True)
            return Response(serializer.data)
        return Response({"error": "organization_id parameter required"}, status=400)


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related('department', 'chair').all()
    serializer_class = ProgramSerializer
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get programs by department ID"""
        dept_id = request.query_params.get('department_id')
        if dept_id:
            programs = self.queryset.filter(department_id=dept_id)
            serializer = self.get_serializer(programs, many=True)
            return Response(serializer.data)
        return Response({"error": "department_id parameter required"}, status=400)


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.select_related('department').all()
    serializer_class = OfficeSerializer
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get offices by department ID"""
        dept_id = request.query_params.get('department_id')
        if dept_id:
            offices = self.queryset.filter(department_id=dept_id)
            serializer = self.get_serializer(offices, many=True)
            return Response(serializer.data)
        return Response({"error": "department_id parameter required"}, status=400)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get positions by type (Academic/Administration)"""
        position_type = request.query_params.get('type')
        if position_type:
            positions = self.queryset.filter(type=position_type)
            serializer = self.get_serializer(positions, many=True)
            return Response(serializer.data)
        return Response({"error": "type parameter required"}, status=400)
