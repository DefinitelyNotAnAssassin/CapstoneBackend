from django.db import models
from leave_requests.models import LeaveRequest


class LeavePackage(models.Model):
    """
    A leave package defines a set of leave credits that can be assigned to an employee.
    Pre-defined packages (e.g., Normal Employee, Newly Hired) and custom packages are supported.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_predefined = models.BooleanField(
        default=False,
        help_text="Predefined packages cannot be deleted by users."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Leave Package'
        verbose_name_plural = 'Leave Packages'

    def __str__(self):
        return self.name


class LeavePackageItem(models.Model):
    """
    Each item represents a leave type and its allocated quantity within a package.
    """
    package = models.ForeignKey(
        LeavePackage,
        on_delete=models.CASCADE,
        related_name='items'
    )
    leave_type = models.CharField(max_length=50, choices=LeaveRequest.LEAVE_TYPES)
    quantity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Number of leave days allocated for this leave type."
    )

    class Meta:
        unique_together = ['package', 'leave_type']
        ordering = ['leave_type']
        verbose_name = 'Leave Package Item'
        verbose_name_plural = 'Leave Package Items'

    def __str__(self):
        return f"{self.package.name} - {self.leave_type}: {self.quantity} days"
