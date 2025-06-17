#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.urls import reverse
from rest_framework.routers import DefaultRouter
from leave_management.views import LeaveRequestViewSet

# Check the available action URLs for LeaveRequestViewSet
router = DefaultRouter()
router.register(r'leave-requests', LeaveRequestViewSet)

print("Available Leave Request URLs:")
for pattern in router.urls:
    print(f"  {pattern.pattern}")

# Try to get the specific URLs
try:
    print("\nSpecific URLs:")
    print(f"my_requests: {reverse('leaverequest-my-requests')}")
    print(f"by_employee: {reverse('leaverequest-by-employee')}")
    print(f"pending_for_approval: {reverse('leaverequest-pending-for-approval')}")
except Exception as e:
    print(f"Error getting URLs: {e}")
