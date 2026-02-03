from django.contrib import admin
from .models import LeavePolicy


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ('leave_type', 'days_allowed', 'description', 'requires_approval', 'requires_documentation')
    search_fields = ('leave_type',)
    list_filter = ('leave_type', 'requires_approval')
