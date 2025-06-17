from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from organizations.models import Organization, Department, Program, Office, Position
from employees.models import (
    Employee, EmployeeEducation, EmployeeSibling, EmployeeDependent,
    EmployeeAward, EmployeeLicense, EmployeeSchedule
)
from leave_management.models import LeavePolicy, LeaveRequest, LeaveCredit, LeaveBalance
from datetime import datetime


class Command(BaseCommand):
    help = 'Import data from frontend data.ts file into Django models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data import...'))

        with transaction.atomic():
            # Import in dependency order
            self.import_organizations()
            self.import_positions()
            self.import_departments()
            self.import_programs()
            self.import_offices()
            self.import_employees()
            self.import_employee_related_data()
            self.import_leave_policies()

        self.stdout.write(self.style.SUCCESS('Data import completed successfully!'))
        self.print_summary()

    def clear_data(self):
        """Clear all existing data"""
        EmployeeEducation.objects.all().delete()
        EmployeeSibling.objects.all().delete()
        EmployeeDependent.objects.all().delete()
        EmployeeAward.objects.all().delete()
        EmployeeLicense.objects.all().delete()
        EmployeeSchedule.objects.all().delete()
        Employee.objects.all().delete()
        LeaveRequest.objects.all().delete()
        LeaveCredit.objects.all().delete()
        LeaveBalance.objects.all().delete()
        LeavePolicy.objects.all().delete()
        Office.objects.all().delete()
        Program.objects.all().delete()
        Department.objects.all().delete()
        Position.objects.all().delete()
        Organization.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

    def import_organizations(self):
        """Import organizations data"""
        organizations_data = [
            {
                'id': 1,
                'name': 'University of Excellence',
                'description': 'A premier educational institution',
                'logo_url': 'https://randomuser.me/api/portraits/lego/1.jpg'
            }
        ]

        for org_data in organizations_data:
            org, created = Organization.objects.get_or_create(
                id=org_data['id'],
                defaults={
                    'name': org_data['name'],
                    'description': org_data['description'],
                    'logo_url': org_data['logo_url']
                }
            )
            if created:
                self.stdout.write(f"Created organization: {org.name}")

    def import_positions(self):
        """Import positions data"""
        positions_data = [
            {'id': 1, 'title': 'Vice President for Academic Affairs', 'type': 'Academic', 'rank': 'VPAA', 'level': 1},
            {'id': 2, 'title': 'Dean', 'type': 'Academic', 'rank': 'DEAN', 'level': 2},
            {'id': 3, 'title': 'Program Chair', 'type': 'Academic', 'rank': 'PC', 'level': 3},
            {'id': 4, 'title': 'Regular Faculty', 'type': 'Academic', 'rank': 'RF', 'level': 4},
            {'id': 5, 'title': 'Part-Time Faculty', 'type': 'Academic', 'rank': 'PTF', 'level': 5},
            {'id': 6, 'title': 'Secretary - Academic', 'type': 'Academic', 'rank': 'SEC', 'level': 6},
            {'id': 7, 'title': 'Vice President', 'type': 'Administration', 'rank': 'VP', 'level': 1},
            {'id': 8, 'title': 'Director', 'type': 'Administration', 'rank': 'DIRECTOR', 'level': 2},
            {'id': 9, 'title': 'Officer', 'type': 'Administration', 'rank': 'OFFICER', 'level': 3},
            {'id': 10, 'title': 'Head', 'type': 'Administration', 'rank': 'HEAD', 'level': 4},
            {'id': 11, 'title': 'Staff', 'type': 'Administration', 'rank': 'STAFF', 'level': 5},
            {'id': 12, 'title': 'Secretary - Admin', 'type': 'Administration', 'rank': 'SEC', 'level': 6},
        ]

        for pos_data in positions_data:
            pos, created = Position.objects.get_or_create(
                id=pos_data['id'],
                defaults=pos_data
            )
            if created:
                self.stdout.write(f"Created position: {pos.title}")

    def import_departments(self):
        """Import departments data"""
        departments_data = [
            {'id': 1, 'name': 'College of Computer Studies', 'organization_id': 1, 'description': 'Department of Computer Science and Information Technology', 'head_id': 3},
            {'id': 2, 'name': 'College of Business', 'organization_id': 1, 'description': 'Department of Business and Management', 'head_id': 8},
            {'id': 3, 'name': 'Administration Department', 'organization_id': 1, 'description': 'Main administrative department', 'head_id': 10},
            {'id': 4, 'name': 'Human Resources', 'organization_id': 1, 'description': 'Human Resources Department', 'head_id': 11},
            {'id': 5, 'name': 'Finance Department', 'organization_id': 1, 'description': 'Finance and Accounting Department', 'head_id': 12},
        ]

        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                id=dept_data['id'],
                defaults={
                    'name': dept_data['name'],
                    'organization_id': dept_data['organization_id'],
                    'description': dept_data['description'],
                    # head will be set after employees are created
                }
            )
            if created:
                self.stdout.write(f"Created department: {dept.name}")

    def import_programs(self):
        """Import programs data"""
        programs_data = [
            {'id': 1, 'name': 'Computer Science', 'department_id': 1, 'description': 'Bachelor of Science in Computer Science', 'chair_id': 4},
            {'id': 2, 'name': 'Information Technology', 'department_id': 1, 'description': 'Bachelor of Science in Information Technology', 'chair_id': 5},
            {'id': 3, 'name': 'Business Administration', 'department_id': 2, 'description': 'Bachelor of Science in Business Administration', 'chair_id': 9},
        ]

        for prog_data in programs_data:
            prog, created = Program.objects.get_or_create(
                id=prog_data['id'],
                defaults={
                    'name': prog_data['name'],
                    'department_id': prog_data['department_id'],
                    'description': prog_data['description'],
                    # chair will be set after employees are created
                }
            )
            if created:
                self.stdout.write(f"Created program: {prog.name}")

    def import_offices(self):
        """Import offices data"""
        offices_data = [
            {'id': 1, 'name': "Dean's Office - CCS", 'department_id': 1, 'location': 'Building A, Room 101', 'extension': '101'},
            {'id': 2, 'name': 'Faculty Room - CCS', 'department_id': 1, 'location': 'Building A, Room 201', 'extension': '201'},
            {'id': 3, 'name': "Dean's Office - Business", 'department_id': 2, 'location': 'Building B, Room 101', 'extension': '301'},
            {'id': 4, 'name': "President's Office", 'department_id': 3, 'location': 'Admin Building, Room 101', 'extension': '401'},
            {'id': 5, 'name': 'HR Office', 'department_id': 4, 'location': 'Admin Building, Room 201', 'extension': '501'},
            {'id': 6, 'name': 'Finance Office', 'department_id': 5, 'location': 'Admin Building, Room 301', 'extension': '601'},
        ]

        for office_data in offices_data:
            office, created = Office.objects.get_or_create(
                id=office_data['id'],
                defaults=office_data
            )
            if created:
                self.stdout.write(f"Created office: {office.name}")

    def import_employees(self):
        """Import employees data"""
        employees_data = [
            # Academic - VPAA
            {
                'id': 1, 'employee_id': 'EMP001', 'first_name': 'Robert', 'middle_name': 'James', 'last_name': 'Williams',
                'suffix': 'PhD', 'nickname': 'Rob', 'present_address': '123 University Ave, Quezon City, Metro Manila',
                'provincial_address': '456 Provincial Rd, Batangas City, Batangas', 'telephone_no': '(02) 8123-4567',
                'mobile_no': '+63 917 123 4567', 'email': 'robert.williams@university.edu',
                'birth_date': '1970-05-15', 'birth_place': 'Manila City', 'age': 53, 'gender': 'Male',
                'citizenship': 'Filipino', 'civil_status': 'Married', 'height': '180 cm', 'weight': '75 kg',
                'ss_no': '11-1111111-1', 'tin_no': '111-111-111-000', 'philhealth_no': '11-111111111-1',
                'pagibig_no': '1111-1111-1111', 'spouse_name': 'Elizabeth Williams', 'spouse_occupation': 'Professor',
                'spouse_company': 'State University', 'father_name': 'George Williams', 'father_occupation': 'Retired Professor',
                'mother_name': 'Mary Williams', 'mother_occupation': 'Retired Teacher',
                'date_hired': '2000-01-15', 'position_id': 1, 'department_id': 1, 'office_id': 1,
                'profile_image': 'https://randomuser.me/api/portraits/men/1.jpg'
            },
            # Academic - Dean of Computer Studies
            {
                'id': 3, 'employee_id': 'EMP003', 'first_name': 'Michael', 'middle_name': 'Thomas', 'last_name': 'Brown',
                'suffix': 'PhD', 'present_address': '789 College St, Makati City, Metro Manila',
                'mobile_no': '+63 917 333 3333', 'email': 'michael.brown@university.edu',
                'birth_date': '1975-08-22', 'birth_place': 'Cebu City', 'age': 48, 'gender': 'Male',
                'citizenship': 'Filipino', 'civil_status': 'Married', 'ss_no': '33-3333333-3', 'tin_no': '333-333-333-000',
                'date_hired': '2005-06-15', 'position_id': 2, 'department_id': 1, 'office_id': 1,
                'profile_image': 'https://randomuser.me/api/portraits/men/3.jpg'
            },
            # Academic - Dean of Business
            {
                'id': 8, 'employee_id': 'EMP008', 'first_name': 'Patricia', 'middle_name': 'Anne', 'last_name': 'Garcia',
                'suffix': 'PhD', 'present_address': '123 Business Ave, Taguig City, Metro Manila',
                'mobile_no': '+63 917 888 8888', 'email': 'patricia.garcia@university.edu',
                'birth_date': '1973-04-12', 'birth_place': 'Manila City', 'age': 50, 'gender': 'Female',
                'citizenship': 'Filipino', 'civil_status': 'Married', 'ss_no': '88-8888888-8', 'tin_no': '888-888-888-000',
                'date_hired': '2006-08-01', 'position_id': 2, 'department_id': 2, 'office_id': 3,
                'profile_image': 'https://randomuser.me/api/portraits/women/8.jpg'
            },
            # Academic - Program Chair of Computer Science
            {
                'id': 4, 'employee_id': 'EMP004', 'first_name': 'Jennifer', 'middle_name': 'Lynn', 'last_name': 'Davis',
                'suffix': 'MS', 'present_address': '456 Tech St, Pasig City, Metro Manila',
                'mobile_no': '+63 917 444 4444', 'email': 'jennifer.davis@university.edu',
                'birth_date': '1980-11-05', 'birth_place': 'Davao City', 'age': 43, 'gender': 'Female',
                'citizenship': 'Filipino', 'civil_status': 'Single', 'ss_no': '44-4444444-4', 'tin_no': '444-444-444-000',
                'date_hired': '2010-08-15', 'position_id': 3, 'department_id': 1, 'office_id': 2, 'program_id': 1,
                'profile_image': 'https://randomuser.me/api/portraits/women/4.jpg'
            },
            # Academic - Program Chair of Information Technology
            {
                'id': 5, 'employee_id': 'EMP005', 'first_name': 'David', 'middle_name': 'Joseph', 'last_name': 'Wilson',
                'suffix': 'MS', 'present_address': '789 IT Blvd, Mandaluyong City, Metro Manila',
                'mobile_no': '+63 917 555 5555', 'email': 'david.wilson@university.edu',
                'birth_date': '1982-03-18', 'birth_place': 'Baguio City', 'age': 41, 'gender': 'Male',
                'citizenship': 'Filipino', 'civil_status': 'Married', 'ss_no': '55-5555555-5', 'tin_no': '555-555-555-000',
                'date_hired': '2012-06-01', 'position_id': 3, 'department_id': 1, 'office_id': 2, 'program_id': 2,
                'profile_image': 'https://randomuser.me/api/portraits/men/5.jpg'
            },
            # Academic - Program Chair of Business Administration
            {
                'id': 9, 'employee_id': 'EMP009', 'first_name': 'Richard', 'middle_name': 'Edward', 'last_name': 'Martinez',
                'suffix': 'MBA', 'present_address': '456 Finance St, Makati City, Metro Manila',
                'mobile_no': '+63 917 999 9999', 'email': 'richard.martinez@university.edu',
                'birth_date': '1978-09-28', 'birth_place': 'Iloilo City', 'age': 45, 'gender': 'Male',
                'citizenship': 'Filipino', 'civil_status': 'Married', 'ss_no': '99-9999999-9', 'tin_no': '999-999-999-000',
                'date_hired': '2008-07-15', 'position_id': 3, 'department_id': 2, 'office_id': 3, 'program_id': 3,
                'profile_image': 'https://randomuser.me/api/portraits/men/9.jpg'
            },
            # Academic - Regular Faculty (Computer Science)
            {
                'id': 6, 'employee_id': 'EMP006', 'first_name': 'Sarah', 'middle_name': 'Elizabeth', 'last_name': 'Anderson',
                'suffix': 'MS', 'present_address': '123 Faculty Row, Quezon City, Metro Manila',
                'mobile_no': '+63 917 666 6666', 'email': 'sarah.anderson@university.edu',
                'birth_date': '1985-07-22', 'birth_place': 'Manila City', 'age': 38, 'gender': 'Female',
                'citizenship': 'Filipino', 'civil_status': 'Single', 'ss_no': '66-6666666-6', 'tin_no': '666-666-666-000',
                'date_hired': '2015-08-01', 'position_id': 4, 'department_id': 1, 'office_id': 2, 'program_id': 1,
                'profile_image': 'https://randomuser.me/api/portraits/women/6.jpg'
            },
            # Academic - Part-Time Faculty (Information Technology)
            {
                'id': 7, 'employee_id': 'EMP007', 'first_name': 'James', 'middle_name': 'Robert', 'last_name': 'Taylor',
                'present_address': '456 Adjunct Ave, Pasig City, Metro Manila',
                'mobile_no': '+63 917 777 7777', 'email': 'james.taylor@university.edu',
                'birth_date': '1988-12-10', 'birth_place': 'Cebu City', 'age': 35, 'gender': 'Male',
                'citizenship': 'Filipino', 'civil_status': 'Single', 'ss_no': '77-7777777-7', 'tin_no': '777-777-777-000',
                'date_hired': '2018-01-15', 'position_id': 5, 'department_id': 1, 'office_id': 2, 'program_id': 2,
                'profile_image': 'https://randomuser.me/api/portraits/men/7.jpg'
            },
            # Administration - VP
            {
                'id': 10, 'employee_id': 'EMP010', 'first_name': 'William', 'middle_name': 'George', 'last_name': 'Thompson',
                'suffix': 'MBA', 'present_address': '789 Executive Blvd, Makati City, Metro Manila',
                'mobile_no': '+63 917 101 0101', 'email': 'william.thompson@university.edu',
                'birth_date': '1968-02-15', 'birth_place': 'Manila City', 'age': 55, 'gender': 'Male',
                'citizenship': 'Filipino', 'civil_status': 'Married', 'ss_no': '10-1010101-0', 'tin_no': '101-010-101-000',
                'date_hired': '2002-03-01', 'position_id': 7, 'department_id': 3, 'office_id': 4,
                'profile_image': 'https://randomuser.me/api/portraits/men/10.jpg'
            },
            # Administration - HR Director
            {
                'id': 11, 'employee_id': 'EMP011', 'first_name': 'Linda', 'middle_name': 'Marie', 'last_name': 'Johnson',
                'suffix': 'MBA', 'present_address': '123 HR Lane, Taguig City, Metro Manila',
                'mobile_no': '+63 917 111 1112', 'email': 'linda.johnson@university.edu',
                'birth_date': '1975-11-30', 'birth_place': 'Bacolod City', 'age': 48, 'gender': 'Female',
                'citizenship': 'Filipino', 'civil_status': 'Married', 'ss_no': '11-1111112-1', 'tin_no': '111-111-112-000',
                'date_hired': '2005-05-15', 'position_id': 8, 'department_id': 4, 'office_id': 5,
                'profile_image': 'https://randomuser.me/api/portraits/women/11.jpg'
            },
            # Administration - Finance Director
            {
                'id': 12, 'employee_id': 'EMP012', 'first_name': 'Robert', 'middle_name': 'John', 'last_name': 'Lee',
                'suffix': 'CPA', 'present_address': '456 Finance Ave, Makati City, Metro Manila',
                'mobile_no': '+63 917 121 2121', 'email': 'robert.lee@university.edu',
                'birth_date': '1973-08-05', 'birth_place': 'Manila City', 'age': 50, 'gender': 'Male',
                'citizenship': 'Filipino', 'civil_status': 'Married', 'ss_no': '12-1212121-2', 'tin_no': '121-212-121-000',
                'date_hired': '2007-07-01', 'position_id': 8, 'department_id': 5, 'office_id': 6,
                'profile_image': 'https://randomuser.me/api/portraits/men/12.jpg'
            },
            # Administration - HR Officer
            {
                'id': 13, 'employee_id': 'EMP013', 'first_name': 'Susan', 'middle_name': 'Elizabeth', 'last_name': 'Clark',
                'present_address': '789 HR Street, Pasig City, Metro Manila',
                'mobile_no': '+63 917 131 3131', 'email': 'susan.clark@university.edu',
                'birth_date': '1985-04-12', 'birth_place': 'Quezon City', 'age': 38, 'gender': 'Female',
                'citizenship': 'Filipino', 'civil_status': 'Single', 'ss_no': '13-1313131-3', 'tin_no': '131-313-131-000',
                'date_hired': '2012-09-01', 'position_id': 9, 'department_id': 4, 'office_id': 5,
                'profile_image': 'https://randomuser.me/api/portraits/women/13.jpg'
            },
            # Administration - Finance Staff
            {
                'id': 14, 'employee_id': 'EMP014', 'first_name': 'John', 'middle_name': 'Michael', 'last_name': 'Rodriguez',
                'present_address': '123 Accounting St, Mandaluyong City, Metro Manila',
                'mobile_no': '+63 917 141 4141', 'email': 'john.rodriguez@university.edu',
                'birth_date': '1990-06-25', 'birth_place': 'Davao City', 'age': 33, 'gender': 'Male',
                'citizenship': 'Filipino', 'civil_status': 'Single', 'ss_no': '14-1414141-4', 'tin_no': '141-414-141-000',
                'date_hired': '2015-03-15', 'position_id': 11, 'department_id': 5, 'office_id': 6,
                'profile_image': 'https://randomuser.me/api/portraits/men/14.jpg'
            },
            # Administration - Secretary (HR)
            {
                'id': 15, 'employee_id': 'EMP015', 'first_name': 'Maria', 'middle_name': 'Teresa', 'last_name': 'Santos',
                'present_address': '456 Secretary Lane, Quezon City, Metro Manila',
                'mobile_no': '+63 917 151 5151', 'email': 'maria.santos@university.edu',
                'birth_date': '1992-09-18', 'birth_place': 'Manila City', 'age': 31, 'gender': 'Female',
                'citizenship': 'Filipino', 'civil_status': 'Single', 'ss_no': '15-1515151-5', 'tin_no': '151-515-151-000',
                'date_hired': '2018-06-01', 'position_id': 12, 'department_id': 4, 'office_id': 5,
                'profile_image': 'https://randomuser.me/api/portraits/women/15.jpg'
            },
            # Academic - Secretary (Computer Studies)
            {
                'id': 16, 'employee_id': 'EMP016', 'first_name': 'Anna', 'middle_name': 'Marie', 'last_name': 'Cruz',
                'present_address': '789 Faculty Circle, Quezon City, Metro Manila',
                'mobile_no': '+63 917 161 6161', 'email': 'anna.cruz@university.edu',
                'birth_date': '1993-11-22', 'birth_place': 'Cebu City', 'age': 30, 'gender': 'Female',
                'citizenship': 'Filipino', 'civil_status': 'Single', 'ss_no': '16-1616161-6', 'tin_no': '161-616-161-000',                'date_hired': '2019-07-15', 'position_id': 6, 'department_id': 1, 'office_id': 1,
                'profile_image': 'https://randomuser.me/api/portraits/women/16.jpg'
            },
        ]

        for emp_data in employees_data:
            # Create user account for each employee
            username = emp_data['email'].split('@')[0]
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': emp_data['email'],
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                }
            )
            if user_created:
                user.set_password('sdca2025')  # Set default password
                user.save()

            # Create employee
            emp, created = Employee.objects.get_or_create(
                id=emp_data['id'],
                defaults={
                    **emp_data,
                    'user': user
                }
            )
            if created:
                # Set the password hash for API authentication
                emp.set_password('sdca2025')
                self.stdout.write(f"Created employee: {emp.first_name} {emp.last_name}")
            else:
                # If employee exists but doesn't have password set, set it
                if not emp.password_hash:
                    emp.set_password('sdca2025')
                    self.stdout.write(f"Updated password for: {emp.first_name} {emp.last_name}")

        # Update department heads and program chairs after employees are created
        self.update_relationships()

    def update_relationships(self):
        """Update department heads and program chairs after employees are created"""
        # Update department heads
        try:
            dept1 = Department.objects.get(id=1)
            dept1.head_id = 3  # Michael Brown
            dept1.save()

            dept2 = Department.objects.get(id=2)
            dept2.head_id = 8  # Patricia Garcia
            dept2.save()

            dept3 = Department.objects.get(id=3)
            dept3.head_id = 10  # William Thompson
            dept3.save()

            dept4 = Department.objects.get(id=4)
            dept4.head_id = 11  # Linda Johnson
            dept4.save()

            dept5 = Department.objects.get(id=5)
            dept5.head_id = 12  # Robert Lee
            dept5.save()

            self.stdout.write("Updated department heads")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not update department heads: {e}"))

        # Update program chairs
        try:
            prog1 = Program.objects.get(id=1)
            prog1.chair_id = 4  # Jennifer Davis
            prog1.save()

            prog2 = Program.objects.get(id=2)
            prog2.chair_id = 5  # David Wilson
            prog2.save()

            prog3 = Program.objects.get(id=3)
            prog3.chair_id = 9  # Richard Martinez
            prog3.save()

            self.stdout.write("Updated program chairs")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not update program chairs: {e}"))

    def import_employee_related_data(self):
        """Import employee siblings, dependents, education, awards, and licenses"""
        
        # Employee siblings
        siblings_data = [
            {'employee_id': 1, 'name': 'James Doe Jr.', 'occupation': 'Software Engineer', 'company': 'Tech Solutions Inc.'},
            {'employee_id': 1, 'name': 'Jennifer Doe', 'occupation': 'Marketing Manager', 'company': 'Global Marketing Co.'},
            {'employee_id': 3, 'name': 'Carlos Cruz', 'occupation': 'Architect', 'company': 'Design Builders Inc.'},
        ]

        for sibling_data in siblings_data:
            EmployeeSibling.objects.get_or_create(
                employee_id=sibling_data['employee_id'],
                name=sibling_data['name'],
                defaults=sibling_data
            )

        # Employee dependents
        dependents_data = [
            {'employee_id': 1, 'name': 'Jake Doe', 'relationship': 'Son', 'occupation': 'Student'},
            {'employee_id': 1, 'name': 'Jessica Doe', 'relationship': 'Daughter', 'occupation': 'Student'},
        ]

        for dependent_data in dependents_data:
            EmployeeDependent.objects.get_or_create(
                employee_id=dependent_data['employee_id'],
                name=dependent_data['name'],
                defaults=dependent_data
            )

        # Employee education
        education_data = [
            {
                'employee_id': 1, 'level': 'Bachelor', 'school': 'University of the Philippines',
                'course': 'Bachelor of Science in Computer Science', 'year_started': '2003',
                'year_ended': '2007', 'graduated': True
            },
            {
                'employee_id': 1, 'level': 'Master', 'school': 'Ateneo de Manila University',
                'course': 'Master of Science in Information Technology', 'year_started': '2010',
                'year_ended': '2012', 'graduated': True
            },
            {
                'employee_id': 14, 'level': 'Bachelor', 'school': 'De La Salle University',
                'course': 'Bachelor of Science in Accountancy', 'year_started': '2008',
                'year_ended': '2012', 'graduated': True
            },
        ]

        for edu_data in education_data:
            EmployeeEducation.objects.get_or_create(
                employee_id=edu_data['employee_id'],
                course=edu_data['course'],
                defaults=edu_data
            )

        # Employee awards
        awards_data = [
            {
                'employee_id': 1, 'name': 'Employee of the Year',
                'awarding_body': 'Company Awards Committee', 'date_awarded': '2022-12-15'
            },
            {
                'employee_id': 14, 'name': 'Outstanding Performance',
                'awarding_body': 'Department of Finance', 'date_awarded': '2021-06-30'
            },
        ]

        for award_data in awards_data:
            EmployeeAward.objects.get_or_create(
                employee_id=award_data['employee_id'],
                name=award_data['name'],
                defaults=award_data
            )

        # Employee licenses
        licenses_data = [
            {
                'employee_id': 14, 'name': 'Certified Public Accountant', 'rating': '85.6',
                'date_taken': '2013-10-05', 'license_no': '0123456',
                'issued_date': '2013-11-15', 'expiration_date': '2026-11-15'
            },
        ]

        for license_data in licenses_data:
            EmployeeLicense.objects.get_or_create(
                employee_id=license_data['employee_id'],
                name=license_data['name'],
                defaults=license_data
            )

        self.stdout.write("Imported employee related data")

    def import_leave_policies(self):
        """Import leave policies"""
        leave_policies_data = [
            {
                'leave_type': 'Vacation Leave', 'days_allowed': 15,
                'description': 'Annual vacation leave for personal time off',
                'requires_approval': True, 'requires_documentation': False,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Sick Leave', 'days_allowed': 15,
                'description': 'Leave for medical reasons',
                'requires_approval': True, 'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Birthday Leave', 'days_allowed': 1,
                'description': 'Leave on or near employee\'s birthday',
                'requires_approval': True, 'requires_documentation': False,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Solo Parent Leave', 'days_allowed': 7,
                'description': 'Additional leave for solo parents',
                'requires_approval': True, 'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Bereavement Leave', 'days_allowed': 5,
                'description': 'Leave for the death of an immediate family member',
                'requires_approval': True, 'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Paternity Leave', 'days_allowed': 7,
                'description': 'Leave for new fathers',
                'requires_approval': True, 'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
            {
                'leave_type': 'Maternity Leave', 'days_allowed': 105,
                'description': 'Leave for new mothers',
                'requires_approval': True, 'requires_documentation': True,
                'applicable_positions': ['Academic', 'Administration']
            },
        ]

        for policy_data in leave_policies_data:
            policy, created = LeavePolicy.objects.get_or_create(
                leave_type=policy_data['leave_type'],
                defaults=policy_data
            )
            if created:
                self.stdout.write(f"Created leave policy: {policy.leave_type}")

    def print_summary(self):
        """Print import summary"""
        self.stdout.write(self.style.SUCCESS("\n=== IMPORT SUMMARY ==="))
        self.stdout.write(f"Organizations: {Organization.objects.count()}")
        self.stdout.write(f"Departments: {Department.objects.count()}")
        self.stdout.write(f"Programs: {Program.objects.count()}")
        self.stdout.write(f"Offices: {Office.objects.count()}")
        self.stdout.write(f"Positions: {Position.objects.count()}")
        self.stdout.write(f"Employees: {Employee.objects.count()}")
        self.stdout.write(f"Employee Education: {EmployeeEducation.objects.count()}")
        self.stdout.write(f"Employee Siblings: {EmployeeSibling.objects.count()}")
        self.stdout.write(f"Employee Dependents: {EmployeeDependent.objects.count()}")
        self.stdout.write(f"Employee Awards: {EmployeeAward.objects.count()}")
        self.stdout.write(f"Employee Licenses: {EmployeeLicense.objects.count()}")
        self.stdout.write(f"Leave Policies: {LeavePolicy.objects.count()}")
        self.stdout.write(f"Users: {User.objects.count()}")
