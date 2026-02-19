from django.core.management.base import BaseCommand
from employee_packages.models import LeavePackage, LeavePackageItem


PREDEFINED_PACKAGES = [
    {
        'name': 'Normal Employee Package',
        'description': 'Standard leave package for regular employees.',
        'items': [
            ('Vacation Leave', 15),
            ('Sick Leave', 15),
            ('Birthday Leave', 1),
            ('Paternity Leave', 15),
        ],
    },
    {
        'name': 'Newly Hired Package',
        'description': 'Reduced leave package for newly hired employees.',
        'items': [
            ('Vacation Leave', 3),
            ('Sick Leave', 3),
            ('Birthday Leave', 1),
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed predefined leave packages (Normal Employee & Newly Hired).'

    def handle(self, *args, **options):
        for pkg_data in PREDEFINED_PACKAGES:
            package, created = LeavePackage.objects.get_or_create(
                name=pkg_data['name'],
                defaults={
                    'description': pkg_data['description'],
                    'is_predefined': True,
                    'is_active': True,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created package: {package.name}"))
            else:
                self.stdout.write(f"Package already exists: {package.name}")

            for leave_type, quantity in pkg_data['items']:
                item, item_created = LeavePackageItem.objects.get_or_create(
                    package=package,
                    leave_type=leave_type,
                    defaults={'quantity': quantity},
                )
                if item_created:
                    self.stdout.write(f"  + {leave_type}: {quantity} days")
                else:
                    self.stdout.write(f"  = {leave_type}: already exists ({item.quantity} days)")

        self.stdout.write(self.style.SUCCESS('Done seeding leave packages.'))
