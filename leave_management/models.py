"""
DEPRECATED: This module is kept for backwards compatibility.
The leave management functionality has been split into separate apps:
- leave_policies: LeavePolicy model
- leave_requests: LeaveRequest model
- leave_credits: LeaveCredit and LeaveBalance models

Import from the new apps instead:
    from leave_policies.models import LeavePolicy
    from leave_requests.models import LeaveRequest
    from leave_credits.models import LeaveCredit, LeaveBalance
"""

# Backwards compatibility imports
from leave_policies.models import LeavePolicy
from leave_requests.models import LeaveRequest
from leave_credits.models import LeaveCredit, LeaveBalance

__all__ = ['LeavePolicy', 'LeaveRequest', 'LeaveCredit', 'LeaveBalance']

