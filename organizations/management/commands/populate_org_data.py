from django.core.management.base import BaseCommand
from organizations.models import Organization, Department, Program, Office, Position


class Command(BaseCommand):
    help = 'Populate the database with initial organization data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate organization data...'))

        # Create Organization
        org, created = Organization.objects.get_or_create(
            name="San Dominic College of Asia",
            defaults={
                'description': "A leading educational institution in Asia",
                'logo_url': "/sdca-logo.png"
            }
        )
        if created:
            self.stdout.write(f"Created organization: {org.name}")
        else:
            self.stdout.write(f"Organization already exists: {org.name}")

        # Create Positions
        positions_data = [
            # Academic Positions
            {'title': 'Vice President for Academic Affairs', 'type': 'Academic', 'rank': 'VPAA', 'level': 1},
            {'title': 'Dean', 'type': 'Academic', 'rank': 'DEAN', 'level': 2},
            {'title': 'Program Chair', 'type': 'Academic', 'rank': 'PC', 'level': 3},
            {'title': 'Regular Faculty', 'type': 'Academic', 'rank': 'RF', 'level': 4},
            {'title': 'Part-time Faculty', 'type': 'Academic', 'rank': 'PTF', 'level': 5},
            {'title': 'Secretary (Academic)', 'type': 'Academic', 'rank': 'SEC', 'level': 6},
            
            # Administrative Positions
            {'title': 'Vice President', 'type': 'Administration', 'rank': 'VP', 'level': 1},
            {'title': 'Director', 'type': 'Administration', 'rank': 'DIRECTOR', 'level': 2},
            {'title': 'Officer', 'type': 'Administration', 'rank': 'OFFICER', 'level': 3},
            {'title': 'Department Head', 'type': 'Administration', 'rank': 'HEAD', 'level': 4},
            {'title': 'Staff', 'type': 'Administration', 'rank': 'STAFF', 'level': 5},
            {'title': 'Secretary (Administrative)', 'type': 'Administration', 'rank': 'SEC', 'level': 6},
        ]

        for pos_data in positions_data:
            pos, created = Position.objects.get_or_create(
                title=pos_data['title'],
                defaults=pos_data
            )
            if created:
                self.stdout.write(f"Created position: {pos.title}")

        # Create Departments
        departments_data = [
            {
                'name': 'College of Computer Studies',
                'description': 'Department focused on computer science and information technology'
            },
            {
                'name': 'College of Business Administration',
                'description': 'Department for business and management programs'
            },
            {
                'name': 'College of Education',
                'description': 'Department for education and teaching programs'
            },
            {
                'name': 'College of Arts and Sciences',
                'description': 'Department for liberal arts and sciences'
            },
            {
                'name': 'Human Resources Department',
                'description': 'Administrative department for human resources'
            },
            {
                'name': 'Finance Department',
                'description': 'Administrative department for finance and accounting'
            },
            {
                'name': 'Registrar Office',
                'description': 'Administrative department for student records'
            },
        ]

        created_departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                organization=org,
                defaults={'description': dept_data['description']}
            )
            created_departments[dept_data['name']] = dept
            if created:
                self.stdout.write(f"Created department: {dept.name}")

        # Create Programs (only for academic departments)
        programs_data = [
            # Computer Studies Programs
            {'name': 'Bachelor of Science in Computer Science', 'department': 'College of Computer Studies'},
            {'name': 'Bachelor of Science in Information Technology', 'department': 'College of Computer Studies'},
            {'name': 'Bachelor of Science in Information Systems', 'department': 'College of Computer Studies'},
            
            # Business Programs
            {'name': 'Bachelor of Science in Business Administration', 'department': 'College of Business Administration'},
            {'name': 'Bachelor of Science in Accountancy', 'department': 'College of Business Administration'},
            {'name': 'Bachelor of Science in Marketing', 'department': 'College of Business Administration'},
            
            # Education Programs
            {'name': 'Bachelor of Elementary Education', 'department': 'College of Education'},
            {'name': 'Bachelor of Secondary Education', 'department': 'College of Education'},
            {'name': 'Master of Arts in Education', 'department': 'College of Education'},
            
            # Arts and Sciences Programs
            {'name': 'Bachelor of Arts in Psychology', 'department': 'College of Arts and Sciences'},
            {'name': 'Bachelor of Science in Mathematics', 'department': 'College of Arts and Sciences'},
            {'name': 'Bachelor of Arts in English', 'department': 'College of Arts and Sciences'},
        ]

        for prog_data in programs_data:
            dept = created_departments[prog_data['department']]
            prog, created = Program.objects.get_or_create(
                name=prog_data['name'],
                department=dept,
                defaults={'description': f"Program under {dept.name}"}
            )
            if created:
                self.stdout.write(f"Created program: {prog.name}")

        # Create Offices
        offices_data = [
            # Computer Studies Offices
            {'name': 'CCS Faculty Office', 'department': 'College of Computer Studies', 'location': 'Building A, 2nd Floor', 'extension': '201'},
            {'name': 'CCS Laboratory', 'department': 'College of Computer Studies', 'location': 'Building A, 3rd Floor', 'extension': '301'},
            
            # Business Offices
            {'name': 'CBA Faculty Office', 'department': 'College of Business Administration', 'location': 'Building B, 2nd Floor', 'extension': '202'},
            {'name': 'CBA Conference Room', 'department': 'College of Business Administration', 'location': 'Building B, 3rd Floor', 'extension': '302'},
            
            # Education Offices
            {'name': 'COE Faculty Office', 'department': 'College of Education', 'location': 'Building C, 2nd Floor', 'extension': '203'},
            {'name': 'COE Resource Center', 'department': 'College of Education', 'location': 'Building C, 1st Floor', 'extension': '103'},
            
            # Arts and Sciences Offices
            {'name': 'CAS Faculty Office', 'department': 'College of Arts and Sciences', 'location': 'Building D, 2nd Floor', 'extension': '204'},
            
            # Administrative Offices
            {'name': 'HR Main Office', 'department': 'Human Resources Department', 'location': 'Administration Building, 1st Floor', 'extension': '101'},
            {'name': 'Finance Office', 'department': 'Finance Department', 'location': 'Administration Building, 2nd Floor', 'extension': '201'},
            {'name': 'Registrar Main Office', 'department': 'Registrar Office', 'location': 'Administration Building, Ground Floor', 'extension': '001'},
        ]

        for office_data in offices_data:
            dept = created_departments[office_data['department']]
            office, created = Office.objects.get_or_create(
                name=office_data['name'],
                department=dept,
                defaults={
                    'location': office_data['location'],
                    'extension': office_data.get('extension', '')
                }
            )
            if created:
                self.stdout.write(f"Created office: {office.name}")

        self.stdout.write(self.style.SUCCESS('Successfully populated organization data!'))
        self.stdout.write(self.style.SUCCESS(f'Organization: {Organization.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Departments: {Department.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Programs: {Program.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Offices: {Office.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Positions: {Position.objects.count()}'))
