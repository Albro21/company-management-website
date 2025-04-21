from django.db import models
from django.utils.text import slugify

from collections import defaultdict


class Company(models.Model):
    COMPANY_TYPES = [
        ('client', 'Client'),
        ('contractor', 'Contractor'),
        ('internal', 'Internal'),
        ('vendor', 'Vendor'),
        ('other', 'Other'),
    ]
    
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

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'companies'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class Role(models.Model):
    company = models.ForeignKey("teams.Company", on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Member(models.Model):
    company = models.ForeignKey("teams.Company", on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    role = models.ForeignKey("teams.Role", on_delete=models.SET_NULL, null=True, blank=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    @property
    def is_active(self):
        return self.user.time_entries.filter(end_time__isnull=True).exists()
    
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
        return f"{self.user.username} ({self.role})"


class JoinRequest(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='join_requests')
    company = models.ForeignKey("teams.Company", on_delete=models.CASCADE, related_name='join_requests')

    class Meta:
        unique_together = ('user', 'company')
    
    def __str__(self):
        return f"Join Request for {self.user.username} → {self.company.name}"
