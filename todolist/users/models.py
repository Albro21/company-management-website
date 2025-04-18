from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    company = models.ForeignKey('teams.Company', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        app_label = 'auth'
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
    def set_company(self, company):
        if self.company != company:
            self.company = company
            self.save()

