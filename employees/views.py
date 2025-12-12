from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
import uuid
from datetime import datetime, timedelta
from .models import (
    Employee, EmployeeEducation, EmployeeSibling, EmployeeDependent,
    EmployeeAward, EmployeeLicense, EmployeeSchedule
)
from .serializers import (
    EmployeeSerializer, EmployeeListSerializer, EmployeeCreateSerializer,
    EmployeeEducationSerializer, EmployeeSiblingSerializer, EmployeeDependentSerializer,
    EmployeeAwardSerializer, EmployeeLicenseSerializer, EmployeeScheduleSerializer
)
from .utils import is_hr_employee


# Simple token storage (in production, use Redis or proper token management)
TOKEN_STORAGE = {}


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related(
        'user', 'position', 'department', 'office', 'program'
    ).prefetch_related(
        'additional_education', 'siblings', 'dependents', 'awards', 'licenses', 'schedules'
    ).all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search employees by name, employee ID, or email"""
        query = request.query_params.get('q', '')
        if query:
            employees = self.queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(middle_name__icontains=query) |
                Q(employee_id__icontains=query) |
                Q(email__icontains=query)
            )
            serializer = EmployeeListSerializer(employees, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get employees by department ID"""
        dept_id = request.query_params.get('department_id')
        if dept_id:
            employees = self.queryset.filter(department_id=dept_id)
            serializer = EmployeeListSerializer(employees, many=True)
            return Response(serializer.data)
        return Response({"error": "department_id parameter required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_position(self, request):
        """Get employees by position ID"""
        position_id = request.query_params.get('position_id')
        if position_id:
            employees = self.queryset.filter(position_id=position_id)
            serializer = EmployeeListSerializer(employees, many=True)
            return Response(serializer.data)
        return Response({"error": "position_id parameter required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get employees by status (active/inactive)"""
        is_active = request.query_params.get('is_active', 'true').lower() == 'true'
        employees = self.queryset.filter(is_active=is_active)
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_email(self, request):
        """Get employee by email"""
        email = request.query_params.get('email')
        if email:
            try:
                employee = self.queryset.get(email=email)
                serializer = self.get_serializer(employee)
                return Response(serializer.data)
            except Employee.DoesNotExist:
                return Response({"error": "Employee not found"}, status=404)
        return Response({"error": "email parameter required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_auth_user(self, request):
        """Get employee by auth user ID"""
        user_id = request.query_params.get('user_id')
        if user_id:
            try:
                employee = self.queryset.get(user__id=user_id)
                serializer = self.get_serializer(employee)
                return Response(serializer.data)
            except Employee.DoesNotExist:
                return Response({"error": "Employee not found"}, status=404)
        return Response({"error": "user_id parameter required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get total employee count"""
        total = self.queryset.count()
        active = self.queryset.filter(is_active=True).count()
        inactive = self.queryset.filter(is_active=False).count()
        return Response({
            "total": total,
            "active": active,
            "inactive": inactive
        })
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better error handling and debugging"""
        print("Employee creation request data:", request.data)
        
        # Ensure dates are in the correct format
        data = request.data.copy()
        
        # Handle date formatting
        for date_field in ['birth_date', 'date_hired']:
            if date_field in data and data[date_field]:
                try:
                    # Try to parse and reformat the date
                    from datetime import datetime
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                        try:
                            dt = datetime.strptime(data[date_field], fmt)
                            data[date_field] = dt.strftime('%Y-%m-%d')
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    print(f"Date parsing error for {date_field}: {e}")
        
        # Provide default password if not supplied
        if 'password' not in data or not data['password']:
            data['password'] = 'sdca2025'
        
        # Create serializer with modified data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                employee = serializer.save()
                print(f"Employee created successfully: {employee}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Employee creation error: {e}")
                return Response(
                    {"error": f"Failed to create employee: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            print("Serializer validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeEducationViewSet(viewsets.ModelViewSet):
    queryset = EmployeeEducation.objects.select_related('employee').all()
    serializer_class = EmployeeEducationSerializer
    
    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return self.queryset.filter(employee_id=employee_id)
        return self.queryset


class EmployeeSiblingViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSibling.objects.select_related('employee').all()
    serializer_class = EmployeeSiblingSerializer
    
    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return self.queryset.filter(employee_id=employee_id)
        return self.queryset


class EmployeeDependentViewSet(viewsets.ModelViewSet):
    queryset = EmployeeDependent.objects.select_related('employee').all()
    serializer_class = EmployeeDependentSerializer
    
    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return self.queryset.filter(employee_id=employee_id)
        return self.queryset


class EmployeeAwardViewSet(viewsets.ModelViewSet):
    queryset = EmployeeAward.objects.select_related('employee').all()
    serializer_class = EmployeeAwardSerializer
    
    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return self.queryset.filter(employee_id=employee_id)
        return self.queryset


class EmployeeLicenseViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLicense.objects.select_related('employee').all()
    serializer_class = EmployeeLicenseSerializer
    
    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return self.queryset.filter(employee_id=employee_id)
        return self.queryset


class EmployeeScheduleViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSchedule.objects.select_related('employee').all()
    serializer_class = EmployeeScheduleSerializer
    
    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return self.queryset.filter(employee_id=employee_id)
        return self.queryset


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Employee login endpoint
    Accepts: {"email": "...", "password": "..."}
    Returns: {"token": "...", "employee": {...}, "user": {...}}
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    print(email, password)
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find employee by email
        employee = Employee.objects.select_related('user', 'position', 'department', 'office').get(
            email=email, is_active=True
        )
        
        # Check password using employee's check_password method
        if employee.check_password(password):
            # Generate a simple token (in production, use JWT or proper token system)
            token = str(uuid.uuid4())
            
            # Store token in both memory and cache (cache persists across restarts)
            TOKEN_STORAGE[token] = employee.id
            
            # Store in cache with 7 days expiry
            cache.set(f'token_{token}', employee.id, timeout=60*60*24*7)
            
            # Also store a reverse mapping for logout
            cache.set(f'employee_{employee.id}_token', token, timeout=60*60*24*7)
            
            print(f"DEBUG login: Stored token for employee {employee.id}: {token[:10]}...")
            print(f"DEBUG login: TOKEN_STORAGE now has {len(TOKEN_STORAGE)} tokens")
            
            # Prepare employee data
            employee_data = {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'first_name': employee.first_name,
                'middle_name': employee.middle_name,
                'last_name': employee.last_name,
                'full_name': employee.full_name,
                'email': employee.email,
                'position_title': employee.position.title if employee.position else '',
                'department_name': employee.department.name if employee.department else '',
                'office_name': employee.office.name if employee.office else '',
                'profile_image': employee.profile_image,
                'is_active': employee.is_active
            }
            
            # Prepare user data
            user_data = {
                'id': employee.user.id if employee.user else None,
                'username': employee.user.username if employee.user else employee.employee_id,
                'email': employee.email,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'is_staff': employee.user.is_staff if employee.user else False,
                'is_superuser': employee.user.is_superuser if employee.user else False
            }
            
            return Response({
                'success': True,
                'token': token,
                'employee': employee_data,
                'user': user_data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Employee.DoesNotExist:
        return Response({
            'error': 'Invalid email or password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            'error': 'An error occurred during login'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    """
    Verify if a token is valid and return employee data
    Accepts: {"token": "..."}
    Returns: {"valid": true/false, "employee": {...}}
    """
    token = request.data.get('token')
    
    if not token:
        return Response({
            'valid': False,
            'error': 'Token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # For demo purposes, we'll accept any UUID-format token
    # In production, implement proper token validation
    try:
        uuid.UUID(token)  # Validate UUID format
        
        # For demo, we'll return a default admin user
        # In production, store and validate actual tokens
        return Response({
            'valid': True,
            'employee': {
                'id': 'demo-admin',
                'employee_id': 'ADMIN001',
                'first_name': 'Admin',
                'last_name': 'User',
                'full_name': 'Admin User',
                'email': 'admin@demo.com',
                'position_title': 'System Administrator',
                'department_name': 'IT Department',
                'office_name': 'Main Office',
                'is_active': True
            },
            'user': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@demo.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        }, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response({
            'valid': False,
            'error': 'Invalid token format'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    """
    Logout endpoint (invalidate token)
    Accepts: {"token": "..."}
    Returns: {"success": true}
    """
    token = request.data.get('token')
    
    if token in TOKEN_STORAGE:
        employee_id = TOKEN_STORAGE[token]
        del TOKEN_STORAGE[token]  # Invalidate the token from memory
        
        # Also clear from cache
        cache.delete(f'token_{token}')
        cache.delete(f'employee_{employee_id}_token')
        
        print(f"DEBUG: Logged out token {token[:10]}... for employee {employee_id}")
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    else:
        # Check if token exists in cache
        employee_id = cache.get(f'token_{token}')
        if employee_id:
            cache.delete(f'token_{token}')
            cache.delete(f'employee_{employee_id}_token')
            
            print(f"DEBUG: Logged out cached token {token[:10]}... for employee {employee_id}")
            
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid or expired token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def demo_login(request):
    """
    Demo login endpoint for admin@demo.com
    Returns demo admin credentials without database lookup
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if email == 'admin@demo.com' and password == 'password':
        token = str(uuid.uuid4())
        
        # Store the demo admin token in TOKEN_STORAGE with a special demo admin ID
        # Find an employee with approval permissions to link to this demo admin
        try:
            # Try to find an employee with VPAA role
            demo_employee = Employee.objects.filter(
                position__rank='VPAA',
                is_active=True
            ).first()
            
            if not demo_employee:
                # If no VPAA, try Dean
                demo_employee = Employee.objects.filter(
                    position__rank='DEAN',
                    is_active=True
                ).first()
            
            if not demo_employee:
                # If no Dean, try PC
                demo_employee = Employee.objects.filter(
                    position__rank='PC',
                    is_active=True
                ).first()
            
            if demo_employee:
                # Store the token linking to this employee for demo purposes
                TOKEN_STORAGE[token] = demo_employee.id
                
                # Also store in cache with 7 days expiry
                cache.set(f'token_{token}', demo_employee.id, timeout=60*60*24*7)
                cache.set(f'employee_{demo_employee.id}_token', token, timeout=60*60*24*7)
                
                print(f"DEBUG: Demo admin token {token[:10]}... stored for employee {demo_employee}")
                print(f"DEBUG: TOKEN_STORAGE now has {len(TOKEN_STORAGE)} tokens")
            else:
                print("DEBUG: No employees with approval permissions found for demo admin")
        except Exception as e:
            print(f"DEBUG: Error setting up demo admin: {e}")
        
        return Response({
            'success': True,
            'token': token,
            'employee': {
                'id': 'demo-admin',
                'employee_id': 'ADMIN001',
                'first_name': 'Admin',
                'last_name': 'User',
                'full_name': 'Admin User',
                'email': 'admin@demo.com',
                'position_title': 'System Administrator',
                'department_name': 'IT Department',
                'office_name': 'Main Office',
                'is_active': True
            },
            'user': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@demo.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            },
            'message': 'Demo login successful'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid demo credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)
