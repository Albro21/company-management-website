from django.db import models
from django.contrib.auth.models import User


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
        
    def __str__(self):
        return self.title


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    title = models.CharField(max_length=200)
    text = models.TextField()
    due_date = models.DateField()

    is_completed = models.BooleanField(default=False)
    is_high_priority = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def complete(self):
        self.is_completed = True
        self.save()

    def toggle_priority(self):
        self.is_high_priority = not self.is_high_priority
        self.save()
