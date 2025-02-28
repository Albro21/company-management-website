from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now, localdate


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    color = ColorField(default='#FFFF00')
        
    def __str__(self):
        return self.title


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    color = ColorField(default='#FFFF00')

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    categories = models.ManyToManyField(Category, blank=True, related_name="tasks")

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
    
    @property
    def is_overdue(self):
        return self.due_date < localdate()

    def complete(self):
        self.is_completed = True
        self.completed_at = now().date()
        self.save()

    def toggle_priority(self):
        self.is_high_priority = not self.is_high_priority
        self.save()
