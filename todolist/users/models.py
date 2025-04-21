from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    company = models.ForeignKey('teams.Company', related_name="company", on_delete=models.SET_NULL, null=True, blank=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
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