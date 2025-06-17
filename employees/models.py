from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver


class Employee(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    CIVIL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced'),
    ]
      # Basic Information
    employee_id = models.CharField(max_length=50, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Password field for API authentication (separate from Django User password)
    password_hash = models.CharField(max_length=128, blank=True, null=True, help_text="Hashed password for API authentication")
    
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=10, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    
    # Contact Information
    present_address = models.TextField()
    provincial_address = models.TextField(blank=True, null=True)
    telephone_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_no = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Personal Information
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    citizenship = models.CharField(max_length=100, default='Filipino')
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES)
    
    # Additional Information
    height = models.CharField(max_length=10, blank=True, null=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    ss_no = models.CharField(max_length=20, blank=True, null=True, verbose_name="SSS Number")
    tin_no = models.CharField(max_length=20, blank=True, null=True, verbose_name="TIN Number")
    philhealth_no = models.CharField(max_length=20, blank=True, null=True, verbose_name="PhilHealth Number")
    pagibig_no = models.CharField(max_length=20, blank=True, null=True, verbose_name="Pag-IBIG Number")
    
    # Family Information
    spouse_name = models.CharField(max_length=255, blank=True, null=True)
    spouse_occupation = models.CharField(max_length=255, blank=True, null=True)
    spouse_company = models.CharField(max_length=255, blank=True, null=True)
    father_name = models.CharField(max_length=255, blank=True, null=True)
    father_occupation = models.CharField(max_length=255, blank=True, null=True)
    father_company = models.CharField(max_length=255, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    mother_occupation = models.CharField(max_length=255, blank=True, null=True)
    mother_company = models.CharField(max_length=255, blank=True, null=True)
    
    # Education Information
    highest_degree = models.CharField(max_length=255, blank=True, null=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    course_or_program = models.CharField(max_length=255, blank=True, null=True)
    year_graduated = models.CharField(max_length=10, blank=True, null=True)
    
    # Employment Information
    date_hired = models.DateField()
    position = models.ForeignKey('organizations.Position', on_delete=models.PROTECT)
    department = models.ForeignKey('organizations.Department', on_delete=models.PROTECT)
    office = models.ForeignKey('organizations.Office', on_delete=models.PROTECT)
    program = models.ForeignKey('organizations.Program', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Profile
    profile_image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
      # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return ' '.join(parts)
    
    @property
    def academic_role_level(self):
        """
        Return academic role level based on position rank:
        0 - VPAA (highest authority)
        1 - Dean
        2 - Program Chair (PC)
        3 - Regular Faculty (RF)
        4 - Part-Time Faculty (PTF)
        5 - Secretary (SEC)
        """
        if self.position and self.position.type == 'Academic':
            rank_mapping = {
                'VPAA': 0,
                'DEAN': 1,
                'PC': 2,
                'RF': 3,
                'PTF': 4,
                'SEC': 5
            }
            return rank_mapping.get(self.position.rank, 6)
        return None
    
    @property
    def can_approve_leaves(self):
        """Check if employee can approve leave requests"""
        return self.academic_role_level is not None and self.academic_role_level <= 2
    
    @property
    def approval_scope(self):
        """
        Determine what level of employees this person can approve leaves for
        VPAA (0): Can approve all
        Dean (1): Can approve PC, Faculty, Secretary in their department
        PC (2): Can approve Faculty and Secretary in their program
        """
        role_level = self.academic_role_level
        if role_level == 0:  # VPAA
            return 'all'
        elif role_level == 1:  # Dean
            return 'department'
        elif role_level == 2:  # PC
            return 'program'
        return 'none'
    
    def can_approve_for_employee(self, target_employee):
        """Check if this employee can approve leaves for the target employee"""
        if not self.can_approve_leaves:
            return False
        
        my_role = self.academic_role_level
        target_role = target_employee.academic_role_level
        
        # Can't approve for higher or equal level positions
        if target_role is not None and target_role <= my_role:
            return False
        
        scope = self.approval_scope
        
        if scope == 'all':
            return True
        elif scope == 'department':
            return self.department == target_employee.department
        elif scope == 'program':
            return (self.program == target_employee.program and 
                   self.program is not None)
        
        return False
    
    class Meta:
        ordering = ['last_name', 'first_name']


class EmployeeEducation(models.Model):
    EDUCATION_LEVELS = [
        ('Elementary', 'Elementary'),
        ('Secondary', 'Secondary'),
        ('Vocational', 'Vocational'),
        ('Bachelor', 'Bachelor'),
        ('Master', 'Master'),
        ('Doctorate', 'Doctorate'),
        ('Other', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='additional_education')
    level = models.CharField(max_length=20, choices=EDUCATION_LEVELS)
    school = models.CharField(max_length=255)
    course = models.CharField(max_length=255, blank=True, null=True)
    year_started = models.CharField(max_length=10)
    year_ended = models.CharField(max_length=10)
    graduated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.level} at {self.school}"
    
    class Meta:
        ordering = ['year_started']


class EmployeeSibling(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='siblings')
    name = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - Sibling: {self.name}"


class EmployeeDependent(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='dependents')
    name = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - Dependent: {self.name}"


class EmployeeAward(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='awards')
    name = models.CharField(max_length=255)
    awarding_body = models.CharField(max_length=255)
    date_awarded = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.name}"


class EmployeeLicense(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='licenses')
    name = models.CharField(max_length=255)
    rating = models.CharField(max_length=50, blank=True, null=True)
    date_taken = models.DateField()
    license_no = models.CharField(max_length=100, blank=True, null=True)
    issued_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.name}"


class EmployeeSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_flexible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.day_of_week}"
    
    class Meta:
        unique_together = ['employee', 'day_of_week']


# Utility methods for Employee model
def create_user_for_employee(employee):
    """Create a Django User for an Employee with default password"""
    if not employee.user:
        # Create username from employee_id or email
        username = employee.employee_id or employee.email.split('@')[0]
        
        # Ensure username is unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=employee.email,
            password='sdca2025',  # Default password
            first_name=employee.first_name,
            last_name=employee.last_name,
            is_active=employee.is_active
        )
        
        # Link the user to the employee
        employee.user = user
        
        # Also set the password hash for API authentication
        employee.password_hash = make_password('sdca2025')
        employee.save()
        
        return user
    return employee.user


@receiver(post_save, sender=Employee)
def create_employee_user(sender, instance, created, **kwargs):
    """Automatically create a User and leave credits when an Employee is created"""
    if created and not instance.user:
        create_user_for_employee(instance)
        # Create initial leave credits for the new employee
        create_initial_leave_credits(instance)
    elif instance.user:
        # Update user information if employee information changes
        instance.user.email = instance.email
        instance.user.first_name = instance.first_name
        instance.user.last_name = instance.last_name
        instance.user.is_active = instance.is_active
        instance.user.save()


# Add method to Employee model for setting password
def set_password(self, raw_password):
    """Set password for the employee (both Django User and API hash)"""
    if self.user:
        self.user.set_password(raw_password)
        self.user.save()
    self.password_hash = make_password(raw_password)
    self.save()

def check_password(self, raw_password):
    """Check password against both Django User and API hash"""
    from django.contrib.auth.hashers import check_password as django_check_password
    
    # Check Django User password first
    if self.user and self.user.check_password(raw_password):
        return True
    
    # Fallback to API password hash
    if self.password_hash:
        return django_check_password(raw_password, self.password_hash)
    
    return False

# Add methods to Employee class
Employee.set_password = set_password
Employee.check_password = check_password

def create_initial_leave_credits(employee):
    """Create initial leave credits for a new employee based on leave policies"""
    from leave_management.models import LeavePolicy, LeaveCredit, LeaveBalance
    from datetime import datetime
    
    current_year = datetime.now().year
    
    # Get all leave policies
    leave_policies = LeavePolicy.objects.all()
    
    for policy in leave_policies:
        # Check if the policy applies to this employee's position type
        # For now, we'll create credits for all policies
        # You can add logic here to check applicable_positions if needed
        
        # Create LeaveCredit record
        leave_credit, created = LeaveCredit.objects.get_or_create(
            employee=employee,
            leave_type=policy.leave_type,
            year=current_year,
            defaults={
                'total_credits': policy.days_allowed,
                'used_credits': 0,
                'remaining_credits': policy.days_allowed,
            }
        )
        
        # Create LeaveBalance record
        leave_balance, created = LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=policy.leave_type,
            defaults={
                'current_balance': policy.days_allowed,
                'accrued_this_year': policy.days_allowed,
                'used_this_year': 0,
                'pending_requests': 0,
            }
        )
