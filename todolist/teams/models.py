# Standard libs
from datetime import timedelta
import os

# Django
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from .choices import *


User = get_user_model()

def document_upload_path(instance, filename):
    full_name = instance.user.get_full_name().replace(' ', '_')
    return f'documents/{full_name}/{filename}'

def receipt_upload_path(instance, filename):
    company = instance.user.company.name
    return f'receipts/{company}/{filename}'

def calculate_weekdays(start_date, end_date):
        delta = timedelta(days=1)
        current = start_date
        count = 0
        while current <= end_date:
            if current.weekday() < 5:
                count += 1
            current += delta
        return count

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
    def pending_holidays(self):
        return self.holidays.filter(status="pending")

    @property
    def pending_edit_holidays(self):
        return self.holidays.filter(status="pending_edit")

    @property
    def pending_delete_holidays(self):
        return self.holidays.filter(status="pending_delete")

    @property
    def total_pending_holidays(self):
        return self.pending_holidays.count() + self.pending_edit_holidays.count() + self.pending_delete_holidays.count()

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


class Document(models.Model):
    DOCUMENT_TYPES = DOCUMENT_TYPES
    
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, default='other')
    file = models.FileField(upload_to=document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def document_name(self):
        return os.path.basename(self.file.name)
    
    def __str__(self):
        return f"{self.user.get_full_name() } - {self.document_type}"
    
    def delete(self, *args, **kwargs):
        if self.file:
            file_path = self.file.path
            if os.path.exists(file_path):
                os.remove(file_path)

        super().delete(*args, **kwargs)


class Expense(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='expenses', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100, blank=True, null=True)
    receipt = models.FileField(upload_to=receipt_upload_path)
    category = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def receipt_name(self):
        return os.path.basename(self.receipt.name)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Expense for {self.user.get_full_name()} on {self.date} ({self.amount}£)"
    
    def delete(self, *args, **kwargs):
        if self.receipt:
            file_path = self.receipt.path
            if os.path.exists(file_path):
                os.remove(file_path)

        super().delete(*args, **kwargs)


class Holiday(models.Model):
    HOLIDAY_TYPES = HOLIDAY_TYPES
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('pending_edit', 'Pending Edit'),
        ('pending_delete', 'Pending Delete')
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='holidays')
    users = models.ManyToManyField("users.CustomUser", related_name='holidays')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(max_length=255)
    type = models.CharField(max_length=50, choices=HOLIDAY_TYPES, default='other')
    paid = models.BooleanField(default=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(default=timezone.now)
    
    # Pending fields to store proposed updates (nullable)
    pending_start_date = models.DateField(null=True, blank=True)
    pending_end_date = models.DateField(null=True, blank=True)
    pending_reason = models.TextField(max_length=255, null=True, blank=True)
    pending_type = models.CharField(max_length=50, choices=HOLIDAY_TYPES, null=True, blank=True)
    pending_paid = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    @property
    def dates(self):
        current = self.start_date
        dates_list = []
        while current <= self.end_date:
            dates_list.append(current)
            current += timedelta(days=1)
        return dates_list

    @property
    def number_of_days(self):
        return calculate_weekdays(self.start_date, self.end_date)

    @property
    def number_of_pending_days(self):
        return calculate_weekdays(self.pending_start_date, self.pending_end_date)

    def clear_pending(self):
        self.pending_start_date = None
        self.pending_end_date = None
        self.pending_reason = None
        self.pending_type = None
        self.pending_paid = None
        self.save()

    def apply_pending(self):
        self.start_date = self.pending_start_date
        self.end_date = self.pending_end_date
        self.reason = self.pending_reason
        self.type = self.pending_type
        self.paid = self.pending_paid
        self.clear_pending()

    def __str__(self):
        return f"{self.start_date} to {self.end_date} ({self.get_type_display()})"


class JoinRequest(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='join_requests', blank=True, null=True)
    company = models.ForeignKey("teams.Company", on_delete=models.CASCADE, related_name='join_requests')

    class Meta:
        unique_together = ('user', 'company')
    
    def __str__(self):
        return f"Join Request for {self.user.get_full_name()} → {self.company.name}"


class Invitation(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=16, unique=True)
    company = models.ForeignKey("teams.Company", on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Invitation for {self.email} by {self.invited_by.email} to join {self.invited_by.company.name}"
