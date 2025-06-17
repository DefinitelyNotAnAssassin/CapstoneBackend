from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Department(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='departments')
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.organization.name}"
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'organization']


class Program(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    description = models.TextField(blank=True, null=True)
    chair = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='chaired_programs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'department']


class Office(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='offices')
    location = models.CharField(max_length=255)
    extension = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'department']


class Position(models.Model):
    POSITION_TYPES = [
        ('Academic', 'Academic'),
        ('Administration', 'Administration'),
    ]
    
    ACADEMIC_RANKS = [
        ('VPAA', 'VPAA'),
        ('DEAN', 'DEAN'),
        ('PC', 'PC'),
        ('RF', 'RF'),
        ('PTF', 'PTF'),
        ('SEC', 'SEC'),
    ]
    
    ADMINISTRATION_RANKS = [
        ('VP', 'VP'),
        ('DIRECTOR', 'DIRECTOR'),
        ('OFFICER', 'OFFICER'),
        ('HEAD', 'HEAD'),
        ('STAFF', 'STAFF'),
        ('SEC', 'SEC'),
    ]
    
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=POSITION_TYPES)
    rank = models.CharField(max_length=20)
    level = models.IntegerField(help_text="Numerical representation of hierarchy level")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.type})"
    
    class Meta:
        ordering = ['level', 'title']
