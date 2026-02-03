from django.core.management.base import BaseCommand
from employees.models import Employee
from leave_policies.models import LeavePolicy
from leave_credits.models import LeaveCredit, LeaveBalance
from datetime import datetime


class Command(BaseCommand):
    help = 'Create leave credits for all existing employees based on leave policies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=datetime.now().year,
            help='Year for which to create leave credits (default: current year)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of leave credits even if they already exist'
        )

    def handle(self, *args, **options):
        year = options['year']
        force = options['force']
        
        self.stdout.write(f'Creating leave credits for year {year}...')
        
        employees = Employee.objects.all()
        leave_policies = LeavePolicy.objects.all()
        
        if not leave_policies.exists():
            self.stdout.write(
                self.style.ERROR('No leave policies found. Please run "create_leave_policies" command first.')
            )
            return
        
        created_credits = 0
        created_balances = 0
        updated_credits = 0
        updated_balances = 0
        
        for employee in employees:
            self.stdout.write(f'Processing employee: {employee.full_name}')
            
            for policy in leave_policies:
                # Create or update LeaveCredit
                credit, created = LeaveCredit.objects.get_or_create(
                    employee=employee,
                    leave_type=policy.leave_type,
                    year=year,
                    defaults={
                        'total_credits': policy.days_allowed,
                        'used_credits': 0,
                        'remaining_credits': policy.days_allowed,
                    }
                )
                
                if created:
                    created_credits += 1
                    self.stdout.write(f'  Created {policy.leave_type} credit: {policy.days_allowed} days')
                elif force:
                    credit.total_credits = policy.days_allowed
                    credit.remaining_credits = credit.total_credits - credit.used_credits
                    credit.save()
                    updated_credits += 1
                    self.stdout.write(f'  Updated {policy.leave_type} credit: {policy.days_allowed} days')
                
                # Create or update LeaveBalance
                balance, created = LeaveBalance.objects.get_or_create(
                    employee=employee,
                    leave_type=policy.leave_type,
                    defaults={
                        'current_balance': policy.days_allowed,
                        'accrued_this_year': policy.days_allowed,
                        'used_this_year': 0,
                        'pending_requests': 0,
                    }
                )
                
                if created:
                    created_balances += 1
                elif force:
                    balance.current_balance = policy.days_allowed
                    balance.accrued_this_year = policy.days_allowed
                    balance.save()
                    updated_balances += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed leave credits:\n'
                f'  Credits: {created_credits} created, {updated_credits} updated\n'
                f'  Balances: {created_balances} created, {updated_balances} updated\n'
                f'  Total employees processed: {employees.count()}'
            )
        )
