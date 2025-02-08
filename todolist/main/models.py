from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    color = ColorField(default='#FFFF00')
        
    def __str__(self):
        return self.title


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = ColorField(default='#FFFF00')

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)

    title = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    due_date = models.DateField()

    is_completed = models.BooleanField(default=False)
    is_high_priority = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return self.title

    def complete(self):
        self.is_completed = True
        self.completed_at = now().date()
        self.save()

    def toggle_priority(self):
        self.is_high_priority = not self.is_high_priority
        self.save()
        
        
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    
    def __str__(self):
        return f"{self.user.username} Profile"
