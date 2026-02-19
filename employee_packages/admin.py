from django.contrib import admin
from .models import LeavePackage, LeavePackageItem


class LeavePackageItemInline(admin.TabularInline):
    model = LeavePackageItem
    extra = 1


@admin.register(LeavePackage)
class LeavePackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'is_predefined', 'created_at')
    list_filter = ('is_active', 'is_predefined')
    search_fields = ('name', 'description')
    inlines = [LeavePackageItemInline]


@admin.register(LeavePackageItem)
class LeavePackageItemAdmin(admin.ModelAdmin):
    list_display = ('package', 'leave_type', 'quantity')
    list_filter = ('package', 'leave_type')
