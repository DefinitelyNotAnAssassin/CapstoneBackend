from django.core.management.base import BaseCommand
from employees.models import Employee, create_initial_leave_credits
from leave_management.models import LeaveCredit, LeaveBalance


class Command(BaseCommand):
    help = 'Generate leave credits for existing employees who don\'t have them'
    # Run this command with: py manage.py generate_leave_credits

    def add_arguments(self, parser):
        parser.add_argument(
            '--employee-id',
            type=str,
            help='Generate leave credits for a specific employee ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regenerate leave credits even if they already exist',
        )

    def handle(self, *args, **options):
        """Generate leave credits for employees"""
        
        if options['employee_id']:
            # Generate for specific employee
            try:
                employee = Employee.objects.get(employee_id=options['employee_id'], is_active=True)
                self.generate_for_employee(employee, options['force'])
            except Employee.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Employee with ID {options["employee_id"]} not found')
                )
                return
        else:
            # Generate for all active employees
            employees = Employee.objects.filter(is_active=True)
            
            self.stdout.write(
                self.style.SUCCESS(f'Processing {employees.count()} active employees...')
            )
            
            processed_count = 0
            skipped_count = 0
            
            for employee in employees:
                if self.generate_for_employee(employee, options['force']):
                    processed_count += 1
                else:
                    skipped_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Completed! {processed_count} employees processed, {skipped_count} skipped'
                )
            )

    def generate_for_employee(self, employee, force=False):
        """Generate leave credits for a single employee"""
        from datetime import datetime
        current_year = datetime.now().year
        
        # Check if employee already has leave credits
        existing_credits = LeaveCredit.objects.filter(
            employee=employee, 
            year=current_year
        ).count()
        
        if existing_credits > 0 and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Skipped {employee.full_name} (ID: {employee.employee_id}) - '
                    f'already has {existing_credits} leave credits for {current_year}'
                )
            )
            return False
        
        if force and existing_credits > 0:
            # Delete existing credits if force is enabled
            LeaveCredit.objects.filter(employee=employee, year=current_year).delete()
            LeaveBalance.objects.filter(employee=employee).delete()
            self.stdout.write(
                self.style.WARNING(
                    f'Deleted existing leave credits for {employee.full_name}'
                )
            )
        
        # Generate leave credits
        try:
            create_initial_leave_credits(employee)
            
            # Count how many were created
            new_credits = LeaveCredit.objects.filter(
                employee=employee, 
                year=current_year
            ).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Generated {new_credits} leave credits for {employee.full_name} '
                    f'(ID: {employee.employee_id})'
                )
            )
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error generating leave credits for {employee.full_name}: {str(e)}'
                )
            )
            return False
