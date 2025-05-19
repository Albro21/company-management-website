# Standard libs
from collections import defaultdict
import pytz
from phonenumber_field.modelfields import PhoneNumberField

# Django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone as tz
from .choices import *


TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]

class CustomUser(AbstractUser):
    EMPLOYEE_STATUSES = EMPLOYEE_STATUSES
    CONTRACT_TYPES = CONTRACT_TYPES
    ROLES = ROLES
    THEMES = THEMES
    
    # Personal
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    date_of_birth = models.DateField(null=True, blank=True)
    mobile_phone = PhoneNumberField(region='GB', blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)
    
    # Work
    company = models.ForeignKey('teams.Company', related_name="employees", on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default='employee')
    job_title = models.ForeignKey("teams.JobTitle", on_delete=models.SET_NULL, blank=True, null=True, related_name="employees")
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPES, default='full_time')
    department = models.CharField(max_length=100, blank=True, null=True)
    supervisor = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subordinates")
    employee_id = models.CharField(max_length=20, blank=True, null=True)
    employee_status = models.CharField(max_length=50, choices=EMPLOYEE_STATUSES, default='active')
    date_of_joining = models.DateField(default=tz.now, blank=True, null=True)
    
    work_email = models.EmailField(blank=True, null=True)
    work_phone = PhoneNumberField(region='GB', blank=True, null=True)
    emergency_phone = PhoneNumberField(region='GB', blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
    
    offline_location = models.CharField(max_length=100, blank=True, null=True)
    offline_workstation_id = models.CharField(max_length=20, blank=True, null=True)
    
    annual_vacation_days = models.PositiveIntegerField(default=20, blank=True)
    used_vacation_days = models.PositiveIntegerField(default=0, blank=True)
    
    probation_start_date = models.DateField(blank=True, null=True)
    probation_end_date = models.DateField(blank=True, null=True)
    
    termination_date = models.DateField(blank=True, null=True)
    termination_reason = models.TextField(blank=True, null=True)
    
    last_promotion_date = models.DateField(blank=True, null=True)
    promotion_reason = models.TextField(blank=True, null=True)
    
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    
    linkedin_url = models.URLField(blank=True, null=True)
    
    # Settings
    theme = models.CharField(max_length=20, choices=THEMES, default='dark')
    timezone = models.CharField(max_length=32, choices=TIMEZONE_CHOICES, default='UTC')


    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = tz.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def personal_projects(self):
        return self.projects.filter(company=None)

    @property
    def company_projects(self):
        if not self.company:
            return []
        return self.company.projects

    @property
    def all_projects(self):
        if not self.company or not self.company.projects.exists():
            return self.personal_projects
        return self.personal_projects.union(self.company.projects.all())
    
    @property
    def is_online(self):
        return self.time_entries.filter(end_time__isnull=True).exists()
    
    @property
    def is_employer(self):
        return self.role == "employer"
    
    @property
    def is_employee(self):
        return self.role == "employee"
    
    @property
    def remaining_vacation_days(self):
        return self.annual_vacation_days - self.used_vacation_days
    
    def hours_spent_by_projects(self, target_date, projects):
        entries = self.time_entries.filter(
            start_time__date=target_date,
            project__in=projects
        ).select_related('project')

        result = defaultdict(float)

        for entry in entries:
            duration = entry.duration.total_seconds() / 3600
            project_title = entry.project.title
            result[project_title] += duration

        return dict(result)
    
    def join_company(self, company, role="employee"):
        self.company = company
        self.role = role
        self.save()
    
    def leave_company(self):
        self.company = None
        self.role = "employee"
        self.job_title = None
        self.contract_type = "full_time"
        self.department = None
        self.supervisor = None
        self.employee_id = None
        self.employee_status = "active"
        self.date_of_joining = None
        self.work_email = None
        self.rate = 0.00
        self.salary = 0.00
        self.offline_location = None
        self.offline_workstation_id = None
        self.annual_vacation_days = 20
        self.used_vacation_days = 0
        self.probation_start_date = None
        self.probation_end_date = None
        self.termination_date = None
        self.termination_reason = None
        self.last_promotion_date = None
        self.promotion_reason = None
        self.save()
    
    def switch_theme(self):
        if self.theme == 'dark':
            self.theme = 'light'
        else:
            self.theme = 'dark'
        self.save()
