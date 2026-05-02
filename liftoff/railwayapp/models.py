from django.db import models


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Departments'


class StaffMember(models.Model):
    staff_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    title = models.CharField(max_length=255, blank=True, null=True)
    date_entered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('vetted', 'Vetted'),
            ('initial_contact', 'Initial Contact'),
        ],
        default='active',
        db_index=True
    )
    employee_type = models.CharField(
        max_length=20,
        choices=[
            ('contractor', 'Contractor'),
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time')
        ],
        default='contractor',
        db_index=True
    )
    contractor_business_name = models.CharField(max_length=255, blank=True, null=True)
    contractor_llc_role = models.CharField(max_length=255, blank=True, null=True)
    rpr_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
    )
    rpr_manager = models.CharField(max_length=255, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    rpr_contract_date = models.DateField(blank=True, null=True)
    contractor_entered_into_adp = models.BooleanField(default=False)
    contractor_paperwork_uploaded = models.BooleanField(default=False)
    proof_of_insurance = models.BooleanField(default=False)
    resume_on_file = models.BooleanField(default=False)
    personal_email = models.EmailField(unique=True)
    business_email = models.EmailField(default="notpopulated@fake.email")
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    contract_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('standby', 'Standby'),
            ('terminated', 'Terminated'),
            ('resigned', 'Resigned')
        ],
        default='active'
    )
    contract_status_date = models.DateField(blank=True, null=True)
    contract_status_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'staffMember'
        indexes = [models.Index(fields=['last_name', 'first_name'])]



class Client(models.Model):
    client_id = models.BigAutoField(primary_key=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active',
        db_index=True
    )
    name = models.CharField(max_length=200)
    rpr_contact = models.ForeignKey(
        StaffMember,
        related_name="rpr_contacts",
        on_delete=models.SET_NULL,
        null=True
    )
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=20)
    contract_date = models.DateField(blank=True, null=True)
    work_orders = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    class Meta:
        db_table = "Client"


class Project(models.Model):
    project_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    client = models.ForeignKey(
        Client,
        related_name="projects",
        on_delete=models.CASCADE,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active',
        db_index=True
    )
    work_orders = models.TextField(blank=True, null=True)
    project_manager = models.CharField(max_length=200)
    project_manager_email = models.EmailField()
    effective_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    reimbursable_expenses = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reimbursable_expenses_notes = models.TextField(blank=True, null=True)
    total_compensation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_compensation_notes = models.TextField(blank=True, null=True)
    invoice_attn = models.CharField(max_length=200, blank=True, null=True)
    invoice_email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = "Projects"


class Assignment(models.Model):
    assignment_id = models.BigAutoField(primary_key=True)
    staff = models.ForeignKey(
        StaffMember,
        related_name="assignments",
        on_delete=models.CASCADE
    )
    project = models.ForeignKey(
        Project,
        related_name="assignments",
        on_delete=models.CASCADE,
        null=True
    )
    invoicing_contact = models.EmailField(blank=True, null=True)
    ap_invoicing_contact = models.EmailField(blank=True, null=True)
    title_from_client = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "Assignment"