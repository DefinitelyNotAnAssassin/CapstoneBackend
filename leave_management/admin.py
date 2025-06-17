from django.contrib import admin
from leave_management.models import (
    LeavePolicy, LeaveRequest, LeaveCredit, LeaveBalance
)   
# Register your models here.
@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ('leave_type', 'days_allowed', 'description', 'requires_approval', 'requires_documentation')
    search_fields = ('leave_type',)
    list_filter = ('leave_type', 'requires_approval')
    
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'leave_type', 'start_date', 'end_date', 
        'days_requested', 'status', 'approved_by', 'approval_date'
    )
    search_fields = ('employee__first_name', 'employee__last_name', 'leave_type')
    list_filter = ('leave_type', 'status', 'start_date', 'end_date')
    date_hierarchy = 'start_date'
    
@admin.register(LeaveCredit)
class LeaveCreditAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'year', 'total_credits', 'used_credits', 'remaining_credits')
    search_fields = ('employee__first_name', 'employee__last_name', 'leave_type')
    list_filter = ('leave_type', 'year')
    ordering = ('-year', 'leave_type')
    
@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'current_balance', 'accrued_this_year', 'used_this_year', 'pending_requests')
    search_fields = ('employee__first_name', 'employee__last_name', 'leave_type')
    list_filter = ('leave_type',)
    ordering = ('employee__first_name', 'employee__last_name', 'leave_type')
