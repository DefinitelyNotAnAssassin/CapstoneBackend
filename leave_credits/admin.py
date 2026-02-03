from django.contrib import admin
from .models import LeaveCredit, LeaveBalance


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
