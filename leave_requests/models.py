from django.db import models


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
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        # Use the same db_table to avoid migrations
        db_table = 'leave_management_leaverequest'
