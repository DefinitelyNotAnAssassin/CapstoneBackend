"""
DEPRECATED: This module is kept for backwards compatibility.
The leave management functionality has been split into separate apps:
- leave_policies: LeavePolicySerializer
- leave_requests: LeaveRequestSerializer, LeaveRequestCreateSerializer, ApprovedByMiniSerializer
- leave_credits: LeaveCreditSerializer, LeaveBalanceSerializer

Import from the new apps instead:
    from leave_policies.serializers import LeavePolicySerializer
    from leave_requests.serializers import LeaveRequestSerializer, LeaveRequestCreateSerializer
    from leave_credits.serializers import LeaveCreditSerializer, LeaveBalanceSerializer
"""

# Backwards compatibility imports
from leave_policies.serializers import LeavePolicySerializer
from leave_requests.serializers import (
    LeaveRequestSerializer,
    LeaveRequestCreateSerializer,
    ApprovedByMiniSerializer
)
from leave_credits.serializers import LeaveCreditSerializer, LeaveBalanceSerializer

__all__ = [
    'LeavePolicySerializer',
    'LeaveRequestSerializer',
    'LeaveRequestCreateSerializer',
    'ApprovedByMiniSerializer',
    'LeaveCreditSerializer',
    'LeaveBalanceSerializer'
]

