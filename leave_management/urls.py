"""
DEPRECATED: This module is kept for backwards compatibility.
The leave management URL configuration has been split into separate apps:
- leave_policies/urls.py: Leave policy endpoints
- leave_requests/urls.py: Leave request endpoints
- leave_credits/urls.py: Leave credit and balance endpoints

For backwards compatibility, this file includes all URLs from the new apps.
"""

from django.urls import path, include

urlpatterns = [
    # Include URLs from new apps for backwards compatibility
    path('', include('leave_policies.urls')),
    path('', include('leave_requests.urls')),
    path('', include('leave_credits.urls')),
]

