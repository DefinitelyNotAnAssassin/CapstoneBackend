from django.contrib import admin
from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'leave_type', 'start_date', 'end_date', 
        'days_requested', 'status', 'approved_by', 'approval_date'
    )
    search_fields = ('employee__first_name', 'employee__last_name', 'leave_type')
    list_filter = ('leave_type', 'status', 'start_date', 'end_date')
    date_hierarchy = 'start_date'
