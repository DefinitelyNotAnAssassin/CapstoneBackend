from django.db import models


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
        verbose_name = 'Leave Policy'
        verbose_name_plural = 'Leave Policies'
        # Use the same db_table to avoid migrations
        db_table = 'leave_management_leavepolicy'
