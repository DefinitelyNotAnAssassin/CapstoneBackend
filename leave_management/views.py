"""
DEPRECATED: This module is kept for backwards compatibility.
The leave management functionality has been split into separate apps:
- leave_policies: LeavePolicyViewSet
- leave_requests: LeaveRequestViewSet and utils
- leave_credits: LeaveCreditViewSet, LeaveBalanceViewSet

Import from the new apps instead:
    from leave_policies.views import LeavePolicyViewSet
    from leave_requests.views import LeaveRequestViewSet
    from leave_requests.utils import get_authenticated_employee, calculate_business_days
    from leave_credits.views import LeaveCreditViewSet, LeaveBalanceViewSet
"""

# Backwards compatibility imports
from leave_policies.views import LeavePolicyViewSet
from leave_requests.views import LeaveRequestViewSet
from leave_requests.utils import get_authenticated_employee, calculate_business_days
from leave_credits.views import LeaveCreditViewSet, LeaveBalanceViewSet

__all__ = [
    'LeavePolicyViewSet',
    'LeaveRequestViewSet',
    'LeaveCreditViewSet',
    'LeaveBalanceViewSet',
    'get_authenticated_employee',
    'calculate_business_days'
]
