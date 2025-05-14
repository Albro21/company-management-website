# Standard libs
from collections import defaultdict
import os
from phonenumber_field.modelfields import PhoneNumberField

# Django
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from .choices import *


def document_upload_path(instance, filename):
    username = instance.member.user.username
    return f'documents/{username}/{filename}'


class Company(models.Model):
    COMPANY_TYPES = COMPANY_TYPES
    
    # Identity
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES, default='other')
    industry = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    # Ownership
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    # Contact
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    
    @property
    def pending_vacation_requests(self):
        return self.vacation_requests.filter(status="pending")

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'companies'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class JobTitle(models.Model):
    company = models.ForeignKey("teams.Company", on_delete=models.CASCADE, related_name="job_titles")
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Member(models.Model):
    EMPLOYEE_STATUSES = EMPLOYEE_STATUSES
    CONTRACT_TYPES = CONTRACT_TYPES
    
    class Role(models.TextChoices):
        EMPLOYER = 'employer', 'Employer'
        EMPLOYEE = 'employee', 'Employee'
    
    company = models.ForeignKey("teams.Company", on_delete=models.CASCADE, related_name="members")
    user = models.OneToOneField("users.CustomUser", on_delete=models.CASCADE, related_name="member")
    supervisor = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subordinates")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
    
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    employee_status = models.CharField(max_length=50, choices=EMPLOYEE_STATUSES, default='active')
    
    job_title = models.ForeignKey("teams.JobTitle", on_delete=models.SET_NULL, blank=True, null=True, related_name="members")   
    department = models.CharField(max_length=100, blank=True, null=True)
    
    mobile_phone = PhoneNumberField(region='GB', blank=True, null=True)
    work_phone = PhoneNumberField(region='GB', blank=True, null=True)
    emergency_phone = PhoneNumberField(region='GB', blank=True, null=True)
    
    personal_email = models.EmailField(blank=True, null=True)
    work_email = models.EmailField(blank=True, null=True)
    
    date_of_joining = models.DateField(default=timezone.now, blank=True, null=True)
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPES, default='full_time')
    
    offline_location = models.CharField(max_length=100, blank=True, null=True)
    offline_workstation_id = models.CharField(max_length=20, blank=True, null=True)
    
    annual_vacation_days = models.PositiveIntegerField(default=20)
    used_vacation_days = models.PositiveIntegerField(default=0)
    
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
    
    @property
    def is_active(self):
        return self.user.time_entries.filter(end_time__isnull=True).exists()
    
    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER
    
    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE
    
    @property
    def remaining_vacation_days(self):
        return self.annual_vacation_days - self.used_vacation_days
    
    def hours_spent_by_projects(self, target_date, projects):
        if projects is None:
            raise ValueError("The 'projects' parameter is required.")

        entries = self.user.time_entries.filter(
            start_time__date=target_date,
            project__in=projects
        ).select_related('project')

        result = defaultdict(float)

        for entry in entries:
            duration = entry.duration.total_seconds() / 3600
            project_title = entry.project.title
            result[project_title] += duration

        return dict(result)
    
    def __str__(self):
        return f"{self.user.username} ({self.job_title})"


class Document(models.Model):
    DOCUMENT_TYPES = DOCUMENT_TYPES
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, default='other')
    file = models.FileField(upload_to=document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def document_name(self):
        return os.path.basename(self.file.name)
    
    def __str__(self):
        return f"{self.member.user.full_name} - {self.document_type}"
    
    def delete(self, *args, **kwargs):
        if self.file:
            file_path = self.file.path
            if os.path.exists(file_path):
                os.remove(file_path)

        super().delete(*args, **kwargs)


class VacationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacation_requests')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='vacation_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-requested_at']
    
    def number_of_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.member.user.username} - {self.start_date} to {self.end_date} ({self.get_status_display()})"


class JoinRequest(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='join_requests')
    company = models.ForeignKey("teams.Company", on_delete=models.CASCADE, related_name='join_requests')

    class Meta:
        unique_together = ('user', 'company')
    
    def __str__(self):
        return f"Join Request for {self.user.username} → {self.company.name}"
