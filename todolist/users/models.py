# Standard libs
import pytz
from phonenumber_field.modelfields import PhoneNumberField

# Django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]

class CustomUser(AbstractUser):
    THEMES = [
        ('dark', 'Dark'),
        ('light', 'Light')
    ]
    
    theme = models.CharField(max_length=20, default='dark', choices=THEMES)
    timezone = models.CharField(max_length=32, choices=TIMEZONE_CHOICES, default='UTC')
    
    company = models.ForeignKey('teams.Company', related_name="company", on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    phone_number = PhoneNumberField(region='GB', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
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
    
    def join_company(self, company):
        self.company = company
        self.save()
    
    def leave_company(self):
        self.member.delete()
        self.company = None
        self.save()
    
    def switch_theme(self):
        if self.theme == 'dark':
            self.theme = 'light'
        else:
            self.theme = 'dark'
        self.save()