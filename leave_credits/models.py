from django.db import models
from leave_requests.models import LeaveRequest


class LeaveCredit(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='leave_credits')
    leave_type = models.CharField(max_length=50, choices=LeaveRequest.LEAVE_TYPES)
    year = models.IntegerField()
    total_credits = models.DecimalField(max_digits=5, decimal_places=2)
    used_credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remaining_credits = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.remaining_credits = self.total_credits - self.used_credits
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} {self.year}: {self.remaining_credits}/{self.total_credits}"
    
    class Meta:
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['-year', 'leave_type']
        verbose_name = 'Leave Credit'
        verbose_name_plural = 'Leave Credits'
        # Use the same db_table to avoid migrations
        db_table = 'leave_management_leavecredit'


class LeaveBalance(models.Model):
    """Current leave balance summary for each employee"""
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.CharField(max_length=50, choices=LeaveRequest.LEAVE_TYPES)
    current_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    accrued_this_year = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    used_this_year = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pending_requests = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type}: {self.current_balance} days"
    
    class Meta:
        unique_together = ['employee', 'leave_type']
        ordering = ['employee', 'leave_type']
        verbose_name = 'Leave Balance'
        verbose_name_plural = 'Leave Balances'
        # Use the same db_table to avoid migrations
        db_table = 'leave_management_leavebalance'
