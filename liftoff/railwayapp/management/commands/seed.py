import random
import string
from django.core.management.base import BaseCommand
from django.db import transaction
from railwayapp.models import Department, StaffMember, Client, Project, Assignment

FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Barbara', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Lisa', 'Daniel', 'Nancy',
    'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Dorothy', 'Paul', 'Kimberly', 'Andrew', 'Emily', 'Kenneth', 'Donna',
    'Joshua', 'Michelle', 'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa',
    'Timothy', 'Deborah', 'Ronald', 'Stephanie', 'Edward', 'Rebecca', 'Jason', 'Sharon',
    'Jeffrey', 'Laura', 'Ryan', 'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Amy',
    'Nicholas', 'Angela', 'Eric', 'Shirley', 'Jonathan', 'Anna', 'Stephen', 'Brenda',
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
    'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts', 'Turner', 'Phillips', 'Evans', 'Parker', 'Edwards', 'Collins',
]

STREETS = [
    '123 Oak St', '456 Maple Ave', '789 Pine Rd', '321 Elm Dr', '654 Cedar Blvd',
    '987 Birch Ln', '147 Walnut St', '258 Chestnut Ave', '369 Spruce Ct', '741 Ash Way',
    '852 Willow Dr', '963 Poplar Rd', '159 Hickory Blvd', '267 Magnolia Ln', '375 Sycamore St',
    '483 Dogwood Ave', '591 Hawthorn Rd', '628 Juniper Dr', '736 Redwood Ct', '844 Cypress Way',
]

CITIES = [
    ('Little Rock', 'AR'), ('Conway', 'AR'), ('Fort Smith', 'AR'), ('Fayetteville', 'AR'),
    ('Jonesboro', 'AR'), ('Texarkana', 'TX'), ('Memphis', 'TN'), ('Nashville', 'TN'),
    ('Dallas', 'TX'), ('Houston', 'TX'), ('Oklahoma City', 'OK'), ('Tulsa', 'OK'),
    ('Jackson', 'MS'), ('Birmingham', 'AL'), ('Montgomery', 'AL'), ('Atlanta', 'GA'),
    ('New Orleans', 'LA'), ('Baton Rouge', 'LA'), ('Springfield', 'MO'), ('Kansas City', 'MO'),
]

COMPANY_SUFFIXES = ['LLC', 'Inc.', 'Corp.', 'Solutions', 'Services', 'Group', 'Consulting', 'Associates']

CLIENT_WORDS = [
    'Apex', 'Summit', 'Horizon', 'Pinnacle', 'Sterling', 'Keystone', 'Vanguard', 'Nexus',
    'Crestwood', 'Ridgeline', 'Ironworks', 'Meridian', 'Cascade', 'Lakeside', 'Clearwater',
    'Redstone', 'Bluegrass', 'Cedarwood', 'Maplewood', 'Riverdale', 'Oakwood', 'Highpoint',
    'Silverado', 'Goldcrest', 'Copperfield', 'Ironbridge', 'Stonewall', 'Bridgewater',
    'Fairview', 'Greenfield', 'Hillcrest', 'Westbrook', 'Eastgate', 'Northridge', 'Southport',
    'Crossroads', 'Cornerstone', 'Landmark', 'Heritage', 'Patriot', 'Pioneer', 'Frontier',
    'Legacy', 'Venture', 'Alliance', 'Titan', 'Atlas', 'Beacon', 'Compass',
]

PROJECT_PREFIXES = [
    'Phase 1 -', 'Phase 2 -', 'Site A -', 'Site B -', 'Q1', 'Q2', 'Q3', 'Q4',
    'Annual', 'Emergency', 'Expansion', 'Renovation', 'Assessment', 'Audit', 'Review',
    'Installation', 'Deployment', 'Upgrade', 'Maintenance', 'Support',
]

TITLES = [
    'Field Technician', 'Project Coordinator', 'Site Inspector', 'Lead Technician',
    'Safety Officer', 'Quality Analyst', 'Operations Specialist', 'Field Engineer',
    'Technical Advisor', 'Site Supervisor', None,
]

STATUSES = ['active', 'inactive', 'vetted', 'initial_contact']
STATUS_WEIGHTS = [60, 15, 15, 10]

CONTRACT_STATUSES = ['active', 'inactive', 'standby', 'terminated', 'resigned']
CONTRACT_WEIGHTS = [55, 15, 15, 10, 5]


def rand_zip():
    return f"{random.randint(10000, 99999)}"


def rand_phone():
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def rand_date(start_year=2018, end_year=2024):
    import datetime
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return start + (end - start) * random.random()


class Command(BaseCommand):
    help = 'Seed the database with fake contractor data'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        Assignment.objects.all().delete()
        Project.objects.all().delete()
        Client.objects.all().delete()
        StaffMember.objects.all().delete()
        Department.objects.all().delete()

        with transaction.atomic():
            # Departments
            self.stdout.write('Creating 4 departments...')
            dept_names = ['Engineering', 'Operations', 'Field Services', 'Quality Assurance']
            departments = [Department.objects.create(name=n) for n in dept_names]

            # Contractors
            self.stdout.write('Creating 276 contractors...')
            used_emails = set()
            contractors = []
            for i in range(276):
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                # ensure unique personal email
                base = f"{first.lower()}.{last.lower()}"
                email = f"{base}@example.com"
                counter = 1
                while email in used_emails:
                    email = f"{base}{counter}@example.com"
                    counter += 1
                used_emails.add(email)

                city, state = random.choice(CITIES)
                has_biz = random.random() < 0.4
                biz_name = f"{last} {random.choice(COMPANY_SUFFIXES)}" if has_biz else None

                contractor = StaffMember(
                    first_name=first,
                    last_name=last,
                    title=random.choice(TITLES),
                    status=random.choices(STATUSES, STATUS_WEIGHTS)[0],
                    employee_type='contractor',
                    contractor_business_name=biz_name,
                    rpr_department=random.choice(departments),
                    rpr_manager=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                    date_of_joining=rand_date(2018, 2023),
                    rpr_contract_date=rand_date(2018, 2023),
                    contractor_entered_into_adp=random.random() < 0.7,
                    contractor_paperwork_uploaded=random.random() < 0.7,
                    proof_of_insurance=random.random() < 0.6,
                    resume_on_file=random.random() < 0.8,
                    personal_email=email,
                    business_email=f"{first.lower()}.{last.lower()}@workmail.com",
                    street=random.choice(STREETS),
                    city=city,
                    state=state,
                    zip_code=rand_zip(),
                    phone_number=rand_phone(),
                    contract_status=random.choices(CONTRACT_STATUSES, CONTRACT_WEIGHTS)[0],
                    contract_status_date=rand_date(2020, 2024),
                    latitude=round(random.uniform(25.0, 49.0), 6),
                    longitude=round(random.uniform(-125.0, -67.0), 6),
                )
                contractors.append(contractor)
            StaffMember.objects.bulk_create(contractors)
            contractors = list(StaffMember.objects.filter(employee_type='contractor'))

            # Clients
            self.stdout.write('Creating 42 clients...')
            clients = []
            used_client_names = set()
            for _ in range(42):
                name = f"{random.choice(CLIENT_WORDS)} {random.choice(COMPANY_SUFFIXES)}"
                while name in used_client_names:
                    name = f"{random.choice(CLIENT_WORDS)} {random.choice(COMPANY_SUFFIXES)}"
                used_client_names.add(name)
                city, state = random.choice(CITIES)
                clients.append(Client(
                    name=name,
                    status=random.choice(['active', 'inactive']),
                    rpr_contact=random.choice(contractors),
                    street=random.choice(STREETS),
                    city=city,
                    state=state,
                    zip_code=rand_zip(),
                    contract_date=rand_date(2019, 2023),
                ))
            Client.objects.bulk_create(clients)
            clients = list(Client.objects.all())

            # Projects
            self.stdout.write('Creating 20 projects...')
            projects = []
            for _ in range(20):
                client = random.choice(clients)
                prefix = random.choice(PROJECT_PREFIXES)
                name = f"{prefix} {client.name.split()[0]} Project"
                city, state = random.choice(CITIES)
                projects.append(Project(
                    name=name,
                    client=client,
                    status=random.choice(['active', 'inactive']),
                    project_manager=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                    project_manager_email=f"pm{random.randint(1,999)}@example.com",
                    effective_date=rand_date(2020, 2024),
                ))
            Project.objects.bulk_create(projects)
            projects = list(Project.objects.all())

            # Assignments
            self.stdout.write('Creating 140 assignments...')
            # pick 140 unique (staff, project) pairs
            pairs = set()
            attempts = 0
            while len(pairs) < 140 and attempts < 10000:
                pairs.add((random.choice(contractors).staff_id, random.choice(projects).project_id))
                attempts += 1

            contractor_map = {c.staff_id: c for c in contractors}
            project_map = {p.project_id: p for p in projects}
            assignments = [
                Assignment(
                    staff=contractor_map[sid],
                    project=project_map[pid],
                    title_from_client=random.choice(TITLES),
                )
                for sid, pid in pairs
            ]
            Assignment.objects.bulk_create(assignments)

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {Department.objects.count()} departments, '
            f'{StaffMember.objects.count()} contractors, '
            f'{Client.objects.count()} clients, '
            f'{Project.objects.count()} projects, '
            f'{Assignment.objects.count()} assignments.'
        ))
