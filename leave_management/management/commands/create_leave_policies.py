from django.core.management.base import BaseCommand
from leave_management.models import LeavePolicy


class Command(BaseCommand):
    help = 'Create default leave policies for the organization'
    # Run this command with: py manage.py create_leave_policies

    def handle(self, *args, **options):
        """Create default leave policies"""
        
        default_policies = [
            {
                'leave_type': 'Vacation Leave',
                'days_allowed': 15,
                'description': 'Annual vacation leave for rest and recreation',
                'requires_approval': True,
                'requires_documentation': False,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Sick Leave',
                'days_allowed': 7,
                'description': 'Leave for illness or medical appointments',
                'requires_approval': True,
                'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Birthday Leave',
                'days_allowed': 1,
                'description': 'Special leave for employee birthday',
                'requires_approval': True,
                'requires_documentation': False,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Solo Parent Leave',
                'days_allowed': 7,
                'description': 'Leave for solo parents to attend to family matters',
                'requires_approval': True,
                'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Bereavement Leave',
                'days_allowed': 3,
                'description': 'Leave for death of immediate family member',
                'requires_approval': True,
                'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Paternity Leave',
                'days_allowed': 7,
                'description': 'Leave for new fathers',
                'requires_approval': True,
                'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Maternity Leave',
                'days_allowed': 105,
                'description': 'Leave for new mothers (15 weeks)',
                'requires_approval': True,
                'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
        ]

        created_count = 0
        updated_count = 0

        for policy_data in default_policies:
            policy, created = LeavePolicy.objects.get_or_create(
                leave_type=policy_data['leave_type'],
                defaults=policy_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created leave policy: {policy.leave_type}')
                )
            else:
                # Update existing policy with new data
                for key, value in policy_data.items():
                    setattr(policy, key, value)
                policy.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated leave policy: {policy.leave_type}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count + updated_count} leave policies '
                f'({created_count} created, {updated_count} updated)'
            )
        )
