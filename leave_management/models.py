from django.db import models
from django.contrib.auth.models import User


class LeavePolicy(models.Model):
    LEAVE_TYPES = [
        ('Vacation Leave', 'Vacation Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Birthday Leave', 'Birthday Leave'),
        ('Solo Parent Leave', 'Solo Parent Leave'),
        ('Bereavement Leave', 'Bereavement Leave'),
        ('Paternity Leave', 'Paternity Leave'),
        ('Maternity Leave', 'Maternity Leave'),
    ]
    
    POSITION_TYPES = [
        ('Academic', 'Academic'),
        ('Administration', 'Administration'),
    ]
    
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES, unique=True)
    days_allowed = models.IntegerField()
    description = models.TextField()
    requires_approval = models.BooleanField(default=True)
    requires_documentation = models.BooleanField(default=False)
    applicable_positions = models.JSONField(default=list)  # Store list of position types
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.leave_type} - {self.days_allowed} days"
    
    class Meta:
        ordering = ['leave_type']


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]
    
    LEAVE_TYPES = [
        ('Vacation Leave', 'Vacation Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Birthday Leave', 'Birthday Leave'),
        ('Solo Parent Leave', 'Solo Parent Leave'),
        ('Bereavement Leave', 'Bereavement Leave'),
        ('Paternity Leave', 'Paternity Leave'),
        ('Maternity Leave', 'Maternity Leave'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Approval fields
    approved_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True, null=True)
    
    # Documentation
    supporting_documents = models.JSONField(default=list, blank=True)  # Store file URLs/paths
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    class Meta:
        ordering = ['-created_at']


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
